"""Define the runtime interface"""
import numpy as np
import textwrap
import copy
import re

import time

import logging

logger = logging.getLogger(__name__)

from femtorun.io_spec import IOSpec, IOSpecLegacyPadding

from typing import *
import numpy.typing as npt

NDARRAYINT = npt.NDArray[int]
NDARRAYINT64 = npt.NDArray[np.uint64]
NDARRAYFLOAT = npt.NDArray[np.float64]
VARVALS = Dict[str, NDARRAYINT]
FVARVALS = Dict[str, NDARRAYFLOAT]
LISTVARVALS = List[Dict[str, NDARRAYINT | NDARRAYFLOAT]]
LEGACYPAD = Optional[Dict[str, Union[int, Tuple[int], Tuple[int, int]]]]
MaybeFVARVALS = Union[VARVALS, FVARVALS]


class FemtoRunner:
    """Supports input/output padding for all derived runtimes

    Derived runners might pad inputs and outputs internally

    Legacy Args (to be deprecated):
        input_padding (dict {varname : (logical len, padded len)}, or None):
          Padding description for inputs; None for no padding
        output_padding (dict {varname : (logical len, padded len)}, or None):
          Padding description for outputs; None for no padding

    Args:
        io_spec (str or IOSpec obj, optional) : file name of IO spec or IO spec object
        pad (bool, default False) : whether or not to pad inputs/unpad outputs
        quantize (bool, default False) : whether or not to quantize inputs/dequantize outputs

    """

    def __init__(
        self,
        input_padding: LEGACYPAD,
        output_padding: LEGACYPAD,
        io_spec: Optional[Union[str, IOSpec]] = None,
        pad: bool = True,
        quantize: bool = False,
    ):
        self.pad = pad
        self.quantize = quantize

        if io_spec is not None:
            if isinstance(io_spec, str):
                self.io = IOSpec(io_spec)
            else:
                self.io = io_spec
        else:
            # temporary, can remove when argument is deprecated/all runners are converted
            if input_padding is not None and output_padding is not None:
                # legacy padding, ignore pad argument
                self.pad = True
                self.io = IOSpecLegacyPadding(input_padding, output_padding)
            else:
                self.pad = False
                self.io = IOSpecLegacyPadding(None, None)
            assert not quantize  # need real IOSpec for this

    def reset(self, reset_vals=None):
        """Reset (or initialize) the runner

        In hardware, this is the hard reset. In a simulation,
        it could mean resetting memory states, metric counters

        The outer reset() function also calls IOSpec's sim_reset()
        """
        self.io.sim_reset()
        self._reset(reset_vals=reset_vals)

    def _reset(self, reset_vals=None):
        """Reset (or initialize) the runner

        In hardware, this is the hard reset. In a simulation,
        it could mean resetting memory states, metric counters
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def finish(self):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def set_vars(self, set_vals):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def get_vars(self, varnames):
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def get_internals(self) -> MaybeFVARVALS:
        """gets all internal variables that are accessible, per runner setup
        implementation will depend on the derived runner, but typically calls get_vars()
        for some set of variables that are monitored

        Does not necessarily need to be implemented. Returns empty by default.
        """
        return {}

    def _quantize_inputs(self, input_vals: MaybeFVARVALS) -> VARVALS:
        """allows easy interoperability between runners that use real-valued inputs
        and those that dont"""

        # AN 11/27/23, working around bug in FS/FX
        # note that all FRs use integers
        cast_input_vals = {}
        for varname, this_input in input_vals.items():
            if np.issubdtype(this_input.dtype, np.integer):
                cast_input_vals[varname] = this_input
            else:
                this_input_as_int = this_input.astype(int)
                was_actually_int = np.allclose(this_input_as_int, this_input)
                if not was_actually_int:
                    raise ValueError(f"nontrivial float->int conversion for {varname}")
                logger.warning(f"converted {varname}, float-of-ints, to int")
                cast_input_vals[varname] = this_input_as_int
        input_vals = cast_input_vals

        if self.quantize:
            # implement me
            input_vals = input_vals
        return input_vals

    def _dequantize_inputs(self, output_vals: VARVALS) -> MaybeFVARVALS:
        """allows easy interoperability between runners that use real-valued outputs
        and those that dont"""
        if self.quantize:
            # implement me
            output_vals = output_vals
        return output_vals

    def _pad_inputs(self, input_vals: VARVALS) -> VARVALS:
        """allows easy interoperability between runners that need padded inputs
        and those that dont"""
        if not self.pad or self.io.input_padding is None:
            return input_vals
        else:
            # pad zeros
            padded = {}

            for varname, vals in input_vals.items():
                valshape = vals.shape
                logicalshape, padshape = self.io.input_padding[varname]

                # FIXME disabled for now, too much weird stuff getting passed in by legacy runners
                # if logicalshape != valshape:
                #    raise ValueError(
                #        f"was passed an input {varname} that had shape {valshape}, expected {logicalshape}"
                #    )

                padded[varname] = np.zeros(padshape, dtype=int)
                if len(valshape) == 1:
                    padded[varname][: valshape[0]] = input_vals[varname]
                elif len(valshape) == 2:
                    padded[varname][: valshape[0], : valshape[1]] = input_vals[varname]
                else:
                    assert False
            return padded

    def _unpad_outputs(self, output_vals: VARVALS) -> VARVALS:
        """allows easy interoperability between runners that need padded outputs
        and those that dont"""
        if not self.pad or self.io.output_padding is None:
            ret = output_vals
        else:
            unpadded = {}
            for varname, vals in output_vals.items():
                logicalshape, padshape = self.io.output_padding[varname]
                if len(padshape) == 1:
                    unpadded[varname] = np.atleast_1d(output_vals[varname])[
                        : logicalshape[0]
                    ]
                elif len(padshape) == 2:
                    unpadded[varname] = np.atleast_2d(output_vals[varname])[
                        : logicalshape[0], : logicalshape[1]
                    ]
                else:
                    assert False
            ret = unpadded
        return ret

    ####################################################
    # low level APIs, akin to AXIS send/recv in HW
    ####################################################

    def send_inputs(self, inputs: MaybeFVARVALS):
        """Send one or more inputs to the runner

        A derived runner will know what computations are performed after these inputs are recv'd,
        and what outputs are produced, if any.

        Derived class may optionally overload (perhaps taking advantage of self.io)
        but it should be sufficient to overload _send_inputs().
        """
        inputs = self._quantize_inputs(self._pad_inputs(inputs))
        self.io.sim_send_inputs(inputs.keys())
        self._send_inputs(inputs)

    def recv_outputs(self) -> MaybeFVARVALS:
        """recv all outputs that have been produced

        This might return an empty VARVALS, if no ouputs were produced given
        previously delivered inputs.

        Derived class may optionally overload (perhaps taking advantage of self.io)
        but it should be sufficient to overload _recv_outputs().
        """
        output_names = self.io.sim_recv_outputs()
        outputs = self._recv_outputs(output_names)
        if output_names is not None and not set(outputs.keys()) == set(output_names):
            raise RuntimeError(
                f"didn't get all expected outputs\nneeded {output_names}\nbut got {outputs.keys()}"
            )
        return self._dequantize_inputs(self._unpad_outputs(outputs))

    def _send_inputs(self, inputs: MaybeFVARVALS):
        """inner implementation of send_inputs, to be overloaded by base class
        The runner's responsibility does not include quantization or padding
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def _wait_for_output(self):
        """wait until an output has been produced.
        On hardware, this is equivalent to waiting until the
        the interrupt pin has been asserted, after the output has been produced.
        On a simulator, it's possible that no action is needed for this function,
        it could just be a pass, or an assertion that execution reached a certain point
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    def _recv_outputs(
        self, expected_output_names: Optional[list[str]]
    ) -> MaybeFVARVALS:
        """inner implementation of recv_outputs, to be overloaded by base class
        The runner's responsibility does not include quantization or padding
        Even though the runner receives the list of output names,
        it should not be necessary in most cases
        (the runner should know which outputs can be delivered).
        It can be used as a check
        """
        raise NotImplementedError("Derived class of FemtoRunner must implement")

    @staticmethod
    def _convert_inputs_to_new_format(
        input_val_timeseries: MaybeFVARVALS | List, allow_2D_vars=False
    ):
        """
        input_val_timeseries: Dict[str, np.ndarray]

        return List[Dict[str, np.ndarray]]

        Checks that the inputs are well-formed, matching VV or LVV format.
        If you get the old style dictionary inputs, check that all variables have the same sequence length.
        We know this is pre-latched input so this has to be true. We then construct a list version to run through
        the simulator just like the new style inputs.
        """

        def _check_varvals(varvals, preamble, D):
            for key, val in varvals.items():
                if not isinstance(val, np.ndarray):
                    raise ValueError(
                        preamble
                        + f"Didn't provide {{varname : {D}D_array(time x dimension)}}, "
                        + f"{key} had something other than {D}D numpy array, type: {type(val)}"
                    )
                if len(val.shape) > D:
                    raise ValueError(
                        preamble
                        + "Didn't provide {{varname : {D}D_array(time x dimension)}}, "
                        + f"{key} had shape {val.shape} ({len(val.shape)}-D, not {D}D)"
                    )

        # first do checking
        if isinstance(input_val_timeseries, dict):
            # check that indexables are all 2D (time x dimensions)
            if allow_2D_vars:
                VV_max_dim = 3
            else:
                VV_max_dim = 2

            _check_varvals(input_val_timeseries, "", VV_max_dim)

            # check that indexables are all the same length
            first_var_vals = next(iter(input_val_timeseries.values()))
            n_steps = first_var_vals.shape[0]

            if not all(
                val.shape[0] == n_steps for val in input_val_timeseries.values()
            ):
                raise ValueError("Input sequence lengths don't match for all variables")

        elif isinstance(input_val_timeseries, list):
            # check that we have a list[dict[1d numpy]]
            for tidx, step_inputs in enumerate(input_val_timeseries):
                preamble = (
                    "Providing a list of timesteps' inputs, "
                    + "but didn't provide [{var_name : 1D_array(var_dimension)}]. "
                )
                if not isinstance(step_inputs, Dict):
                    raise ValueError(
                        preamble
                        + f"At step {tidx}, didn't have a dictionary, had {type(step_inputs)}. "
                    )

                if allow_2D_vars:
                    LVV_max_dim = 2
                else:
                    LVV_max_dim = 1

                _check_varvals(
                    step_inputs,
                    preamble + f"At step {tidx}, had a problem: ",
                    LVV_max_dim,
                )

        else:
            raise ValueError(
                "Need to provide either: [{var_name : 1D_array(var_dimension)}], "
                + "or {varname : 2D_array(time x dimension)}. "
                + f"Instead, got {type(input_val_timeseries)}"
            )

        # now do conversion
        if isinstance(input_val_timeseries, dict):
            first_var_vals = next(iter(input_val_timeseries.values()))
            n_steps = first_var_vals.shape[0]

            list_var_vals = [
                {key: val[i] for key, val in input_val_timeseries.items()}
                for i in range(n_steps)
            ]
        else:
            list_var_vals = input_val_timeseries

        return list_var_vals

    @staticmethod
    def _convert_output_to_old_format(var):
        return {key: np.stack([d[key] for d in var]) for key in var[0].keys()}

    ####################################################
    # higher-level APIs
    ####################################################

    def step(self, input_vals: MaybeFVARVALS) -> tuple[MaybeFVARVALS, MaybeFVARVALS]:
        """for models with only a single simple_sequence in their spec,
        execute one timestep, driving input_vals and getting outputs

        Args:
            input_vals (dict {varname (str): val (1d numpy.ndarray)):
                Variable names and their values for one timestep

        Returns:
            (output_vals, internal_vals) tuple(dict, dict)):
                tuple of dictionaries with same format as input_vals,
                Output variables and their values, and
                internal variables and their values
        """
        if not self.io.is_simple:
            raise RuntimeError(
                "tried to call step() (or run()) for a FemtoRunner with a more complex IO spec. step() is only for networks with 'function-style' inputs->step->outputs dependency."
            )

        self.send_inputs(input_vals)
        internals = self.get_internals()
        return self.recv_outputs(), internals

    def run(
        self,
        input_val_timeseries: MaybeFVARVALS | LISTVARVALS,
    ) -> Union[
        tuple[VARVALS, VARVALS, None],
        tuple[FVARVALS, FVARVALS, None],
        tuple[LISTVARVALS, LISTVARVALS, None],
    ]:
        """Execute several timesteps, iterating through the values of input_val_timeseries
        driving the runner at each timestep. Calls .step() each timestep.

        Args:
            input_val_timeseries (dict {varname (str): value (numpy.ndarray)}):
                keyed by variable names, values are 2d numpy arrays, first dim is time

        Returns:
            (output_vals, internal_vals, None) tuple(dict, dict, dict)):
                tuple of dictionaries with same format as input_vals,
                values for the output variables as well as all internal variables,
                for all timesteps that were run
        """

        # convert to list[dict[array]] format, if input is dict[2darray]
        list_var_vals = FemtoRunner._convert_inputs_to_new_format(input_val_timeseries)

        #### New check to make sure that the shape of each input is the same across all the timesteps
        vars_to_shape = {}

        for timestep in list_var_vals:
            for var in timestep:
                if var not in vars_to_shape:
                    vars_to_shape[var] = timestep[var].shape
                if not timestep[var].shape == vars_to_shape[var]:
                    raise ValueError(
                        f"The shape of {var} is not the same across timesteps."
                    )
        ############################################################################################

        # run simulation, calling step, building up lists for outputs and internal states
        output_vals = []
        internal_vals = []

        for i, step_inputs in enumerate(list_var_vals):
            step_out, step_internals = self.step(step_inputs)

            output_vals.append(copy.deepcopy(step_out))
            internal_vals.append(copy.deepcopy(step_internals))

        # convert back to dict[2darray] if input had that format
        if isinstance(input_val_timeseries, Dict):
            output_vals = FemtoRunner._convert_output_to_old_format(output_vals)
            internal_vals = FemtoRunner._convert_output_to_old_format(internal_vals)

        # note, third return value is deprecated, to be removed
        return output_vals, internal_vals, None

    @classmethod
    def compare_outputs(
        cls,
        name_A: str,
        output_A: LISTVARVALS,
        name_B: str,
        output_B: LISTVARVALS,
        error_tolerance: Optional[Union[float, int]] = None,
        logstr: str = "compare_outputs",
        allow_2D_vars=False,
    ) -> int:
        """
        Compare two list-of-dicts sequences containing np.ndarray values.

        Rules
        -----
        * Same key set is **required** (compare_internals already enforces this).
        * Rank must match.
        * If more than one axis length differs → error.
        * If exactly one axis length differs → slice both arrays to
        `min(dim_A, dim_B)` on that axis and compare values.
        * Optional absolute `error_tolerance`.
        * Returns 0 on success, −1 on any mismatch (shape or value).
        """

        # convert to list[dict[array]] format, if input is dict[2darray]
        output_A = FemtoRunner._convert_inputs_to_new_format(
            output_A, allow_2D_vars=allow_2D_vars
        )
        output_B = FemtoRunner._convert_inputs_to_new_format(
            output_B, allow_2D_vars=allow_2D_vars
        )

        # Check lengths
        if len(output_A) != len(output_B):
            logger.error(
                f"{logstr}: length mismatch: {name_A} has {len(output_A)} elements, "
                f"{name_B} has {len(output_B)} elements"
            )
            return -1

        n_steps = len(output_A)

        # Collect shape info for debug output
        shape_dict_A = {
            f"step_{i}": {k: v.shape for k, v in output_A[i].items()}
            for i in range(n_steps)
        }
        shape_dict_B = {
            f"step_{i}": {k: v.shape for k, v in output_B[i].items()}
            for i in range(n_steps)
        }
        contents_str = (
            f"{logstr}: {name_A} vs {name_B}\n"
            f"{name_A} shapes:\n{textwrap.indent(str(shape_dict_A), '  ')}\n"
            f"{name_B} shapes:\n{textwrap.indent(str(shape_dict_B), '  ')}\n"
        )

        ####################################### keys #################################
        # Check keys at each timestep
        for i, (dict1, dict2) in enumerate(zip(output_A, output_B)):
            keys1 = set(dict1.keys())
            keys2 = set(dict2.keys())

            if keys1 != keys2:
                logger.debug(contents_str)
                missing_in_dict2 = keys1 - keys2
                missing_in_dict1 = keys2 - keys1

                error_msg = (
                    f"Key mismatch at timestep {i} between {name_A} and {name_B}\n"
                )
                if missing_in_dict2:
                    error_msg += f"  {name_A} has keys not in {name_B}: {sorted(missing_in_dict2)}\n"
                if missing_in_dict1:
                    error_msg += f"  {name_B} has keys not in {name_A}: {sorted(missing_in_dict1)}\n"
                logger.error(error_msg)
                return -1

        #################################### shapes ##################################
        bad_shape_multi, bad_shape_rank = [], []
        slice_spec = {}  # per-(timestep, key) slice tuples (Ellipsis == exact match)

        for step_idx in range(n_steps):
            dict_A = output_A[step_idx]
            dict_B = output_B[step_idx]

            for k in dict_A:
                a, b = dict_A[k], dict_B[k]

                # Check if both are numpy arrays
                if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
                    logger.error(
                        f"At timestep {step_idx}, key '{k}': values are not both numpy arrays"
                    )
                    return -1

                if a.ndim != b.ndim:
                    bad_shape_rank.append((step_idx, k, a.shape, b.shape))
                    continue

                diff_axes = [
                    i for i, (sa, sb) in enumerate(zip(a.shape, b.shape)) if sa != sb
                ]

                if len(diff_axes) == 0:  # identical
                    slice_spec[(step_idx, k)] = (Ellipsis,)
                elif len(diff_axes) == 1:  # one-axis mismatch → make slice
                    ax = diff_axes[0]
                    overlap = min(a.shape[ax], b.shape[ax])
                    slicer = [slice(None)] * a.ndim
                    slicer[ax] = slice(0, overlap)
                    slice_spec[(step_idx, k)] = tuple(slicer)
                else:  # >1 axis mismatch
                    bad_shape_multi.append((step_idx, k, a.shape, b.shape))

        if bad_shape_rank or bad_shape_multi:
            msg = "Shape mismatches:\n"
            for step_idx, k, sA, sB in bad_shape_rank:
                msg += f"  timestep {step_idx}, {k}: rank differs {sA} vs {sB}\n"
            for step_idx, k, sA, sB in bad_shape_multi:
                msg += f"  timestep {step_idx}, {k}: >1 axis differ {sA} vs {sB}\n"
            logger.debug(contents_str)
            logger.error(msg)

        # ------------------------------------------------------------- values
        bad_value = []

        for step_idx in range(n_steps):
            dict_A = output_A[step_idx]
            dict_B = output_B[step_idx]

            for k in dict_A:
                a, b = dict_A[k], dict_B[k]

                # skip this var if shape problem previously caught
                shapekey = (step_idx, k, a.shape, b.shape)
                if shapekey in bad_shape_rank or shapekey in bad_shape_multi:
                    continue

                sl = slice_spec[(step_idx, k)]
                a_sub, b_sub = a[sl], b[sl]

                if error_tolerance is None:
                    equal = np.all(a_sub == b_sub)
                else:
                    equal = np.all(np.abs(a_sub - b_sub) <= error_tolerance)

                if not equal:
                    bad_value.append(
                        {
                            "step_idx": step_idx,
                            "key": k,
                            "shape_A": a.shape,
                            "shape_B": b.shape,
                            "value_A": a_sub,
                            "value_B": b_sub,
                            "diff": a_sub - b_sub,
                        }
                    )

        if bad_value:
            msg = "Value mismatches:\n"
            for mismatch in bad_value:
                msg += f"  timestep {mismatch['step_idx']}, {mismatch['key']}: compared over "
                msg += (
                    "full shape "
                    if mismatch["shape_A"] == mismatch["shape_B"]
                    else "overlapping slice "
                )
                msg += f"{mismatch['shape_A']} vs {mismatch['shape_B']}\n"

            msg += "these were the mismatches:\n"
            for mismatch in bad_value:
                msg += f"t = {mismatch['step_idx']}, {mismatch['key']} :\n"
                msg += f"  {name_A} had:\n"
                msg += f"{textwrap.indent(str(mismatch['value_A']), '    ')}\n"
                msg += f"  {name_B} had:\n"
                msg += f"{textwrap.indent(str(mismatch['value_B']), '    ')}\n"
                msg += f"  difference ({name_A} - {name_B}):\n"
                msg += f"{textwrap.indent(str(mismatch['diff']), '    ')}\n"

            logger.debug(contents_str)
            logger.error(msg)
            return -1

        logger.debug(f"{logstr} succeeded")
        return 0

    @classmethod
    def _sortkey(cls, x):
        endnum = re.search(r"\d+$", x)
        if endnum:
            return int(endnum.group())
        else:
            return 0  # others wind up in random order

    @classmethod
    def compare_internals(
        cls,
        name_A: str,
        output_A: LISTVARVALS,
        name_B: str,
        output_B: LISTVARVALS,
        error_tolerance: Optional[Union[float, int]] = None,
        allow_2D_vars=True,
    ) -> int:
        """
        Compare only the tensors that appear in *both* list-of-dicts sequences.

        • First checks that sequences have the same length.
        • `compare_outputs` is still called first - so shape-mismatch diagnostics
          stay exactly the same.
        • We then run a second pass that:
            - Ignores rank mismatches and >1-axis shape mismatches.
            - Slices both tensors to the overlapping extent when exactly one axis
              differs.
            - Collects any *value* mismatches and prints a full dump.
            - If no value mismatches are found it logs an INFO message.
        • Return value is -1 if *either* the first or second pass found a
          mismatch, otherwise 0.
        """

        # convert to list[dict[array]] format, if input is dict[2darray]
        output_A = FemtoRunner._convert_inputs_to_new_format(
            output_A, allow_2D_vars=allow_2D_vars
        )
        output_B = FemtoRunner._convert_inputs_to_new_format(
            output_B, allow_2D_vars=allow_2D_vars
        )

        # ------------------------------- check sequence lengths ------------------
        if len(output_A) != len(output_B):
            logger.error(
                f"Sequence length mismatch: {name_A} has {len(output_A)} timesteps, "
                f"{name_B} has {len(output_B)} timesteps"
            )
            return -1

        # -------------------------------get common keys ------------------
        # Get keys that appear in all timesteps of both sequences
        keys_A_all = (
            set.intersection(*[set(d.keys()) for d in output_A]) if output_A else set()
        )
        keys_B_all = (
            set.intersection(*[set(d.keys()) for d in output_B]) if output_B else set()
        )
        if keys_A_all == keys_B_all:
            # if perfect match, keep order, user probably chose the set themselves
            # with compare_runs.internal_var_order
            key_points = output_A[0].keys()
        else:
            key_points = set(sorted(keys_A_all & keys_B_all, key=cls._sortkey))

        def _print_keys(pre: str, keys: set[str]):
            logger.info(pre)
            for k in keys:
                logger.info(f"  {k}")

        logger.info("Comparing Internal Values")
        _print_keys("Key Points:", key_points)
        _print_keys(
            f"{name_A}-only vars (NOT compared):", sorted(keys_A_all - key_points)
        )
        _print_keys(
            f"{name_B}-only vars (NOT compared):", sorted(keys_B_all - key_points)
        )

        # -------------------------------compare ------------------
        # trim A, B down to key points, pass through compare_outputs
        def _trim_to_key_points(output, keys):
            trimmed = []
            for step_vals in output:
                trimmed.append({k: step_vals[k] for k in keys})
            return trimmed

        key_output_A = _trim_to_key_points(output_A, key_points)
        key_output_B = _trim_to_key_points(output_B, key_points)

        return cls.compare_outputs(
            name_A,
            key_output_A,
            name_B,
            key_output_B,
            error_tolerance,
            logstr="compare_internals",
            allow_2D_vars=True,
        )

    @classmethod
    def compare_runs(
        cls,
        inputs: VARVALS,
        *runners,
        names: Optional[List[str]] = None,
        compare_internals: bool = False,
        except_on_error: bool = True,
        error_tolerance: Optional[Union[float, int]] = None,
        no_reset: bool = False,
        compare_status: Optional[Dict] = None,
        internal_var_order: Optional[List[str]] = None,
    ):
        """run two FemtoRunners next to each other and compare the outputs

        doesn't compare internal states, which can be hard to generalize, returns them instead

        Args:
            inputs : (dict) : same format to FemtoRunne.run()
            *runners : (variable number of :obj:`FemtoRunner`) : the FemtoRunners to compare
            compare_internals : also check internal variables values' match
            internal_var_order : for internal comparison, only check these vars, and report in the same order
        """
        np.set_printoptions(threshold=10000)

        if names is None:
            names = [runner.__class__.__name__ for runner in runners]
        assert len(names) == len(runners)

        inputs = FemtoRunner._convert_inputs_to_new_format(inputs)

        outs = []
        internals = []
        durs = []

        def run_one(name, runner):
            t0 = time.time()

            try:
                if not no_reset:
                    runner.reset()

                out, internal, _ = runner.run(inputs)
                outs.append(out)

                # filter internal vals, if internal_var_order was provided
                # this also puts them in order
                if internal_var_order is not None:
                    filtered_internals = []
                    for internal_timestep in internal:
                        filtered_internals.append(
                            {k: internal_timestep[k] for k in internal_var_order}
                        )
                    internals.append(filtered_internals)
                else:
                    internals.append(internal)

                runner.finish()
            except:
                runner.finish()  # we need to try to exit cleanly for some runners, notably FB's SimRunner
                raise

            tdur = time.time() - t0
            durs.append(tdur)

        for name, runner in zip(names, runners):
            run_one(name, runner)

        saw_err = False
        for name, runner, out in zip(names[1:], runners[1:], outs[1:]):
            err = FemtoRunner.compare_outputs(
                names[0], outs[0], name, out, error_tolerance
            )
            saw_err = saw_err or (err != 0)
            if not saw_err:
                logger.info(
                    "Output comparison succeeded! checking internal key points (if supplied)"
                )

            if err:
                # if the output didn't match, run the internal comparison anyway for debug purposes
                logger.info(
                    "Output comparison failed! checking internal key points (if supplied)"
                )
                for name, runner, out in zip(names[1:], runners[1:], internals[1:]):
                    FemtoRunner.compare_internals(
                        names[0], internals[0], name, out, error_tolerance
                    )

        saw_internal_err = False
        if compare_internals:
            # check internal values that name-match
            for name, runner, out in zip(names[1:], runners[1:], internals[1:]):
                err = FemtoRunner.compare_internals(
                    names[0], internals[0], name, out, error_tolerance
                )
                saw_internal_err = saw_internal_err or (err != 0)

        if saw_err:
            status_str = "OUTPUT COMPARISONS FAILED! See log\n"
            final_log = logger.error
        elif not saw_err and saw_internal_err:
            status_str = (
                "Output comparison succeeded, BUT internal points differ! See log\n"
            )
            final_log = logger.warning
        else:
            status_str = "Comparison of these runners SUCCEEDED!:\n"
            final_log = logger.info

        for name, runner, dur in zip(names, runners, durs):
            status_str += textwrap.indent(f"{name} : took {round(dur, 2)} s\n", "  ")
        final_log(status_str)

        if (saw_err or saw_internal_err) and except_on_error:
            raise ValueError(status_str)

        # fill pass by ref compare_status dict
        if compare_status is not None:
            compare_status["pass"] = not saw_err
            compare_status["status_str"] = status_str

        np.set_printoptions(threshold=1000)  # the default, put it back

        def _rekey(x):
            return {n: vals for n, vals in zip(names, x)}

        # rekey from runner index to supplied name for convenience
        return _rekey(outs), _rekey(internals)


class ComposedRunner(FemtoRunner):
    """create a new FemtoRunner object that strings one or more runners together

    The port maps allow for hooking up output names to input names

    Args:
        list_of_runners : (list of :obj:`FemtoRunner`) :
            list of femtorunners to stack in a sequence
        list_of_port_maps : (list of dicts, or None) :
            list of port maps, or None where a port map is not needed
            must be the same length as list_of_runners
            individual list elements may also be None if no mapping is needed for that layer
            [{output_i_name : input_i+1_name, ...}, ...]
    """

    def __init__(self, list_of_runners, list_of_port_maps=None):
        self.runners = list_of_runners
        self.port_maps = list_of_port_maps

    def reset(self, reset_vals=None):
        for runner in self.runners():
            runner.reset(reset_vals)

    def finish(self):
        for runner in self.runners:
            runner.finish()

    def step(self, input_vals):
        layer_inputs = input_vals
        all_internals = {}
        for i, runner in enumerate(self.runners):
            outputs, internals = runner.step(layer_inputs)

            if self.port_maps is not None and self.port_maps[i] is not None:
                layer_inputs = {}
                port_map = self.port_maps[i]
                for k, v in outputs.items():
                    layer_inputs[port_map[k]] = v
            else:
                layer_inputs = outputs

            for k, v in internals:
                if k in all_internals:
                    raise NotImplementedError(
                        "colliding state names in ComposedRunner, need to deal with this somehow"
                    )
                all_internals[k] = v

        return layer_inputs, all_internals

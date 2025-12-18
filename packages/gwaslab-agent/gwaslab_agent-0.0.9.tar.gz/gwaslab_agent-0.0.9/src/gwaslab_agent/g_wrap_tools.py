import pandas as pd
import json
import numpy as np
from numbers import Number
import traceback
import inspect
import gwaslab as gl
from gwaslab_agent.g_image import _scrub_log
from gwaslab_agent.g_image import _show_locally
from gwaslab_agent.g_image import _is_figure
from gwaslab_agent.g_tools import FILTERER_SET
from gwaslab_agent.g_warp_tools_helper import (
    _success_json,
    _df_payload,
    _series_payload,
    _ndarray_payload,
    _list_tuple_payload,
    _resolve_df_value,
    build_payload_for_result,
    build_error_payload,
    prepare_kwargs,
    image_payload,
    sumstats_payload,
)

def wrap_loader_method(self, name, method):
    def wrapped(**kwargs):
        try:
            previous_log_end = len(self.log.log_text)
            result = method(**kwargs)
            self.archive.append(result)
            new_log = self.log.log_text[previous_log_end:]
            
            if isinstance(result, gl.Sumstats):
                out_type = "gl.Sumstats"
                data_string = "Sumstats has been successfully loaded."
                self.sumstats.data = result.data
                self.sumstats.meta = result.meta
                self.sumstats.build = result.build
                self.log.combine(result.log,pre=False)
                new_log = self.log.log_text[previous_log_end + 1:]
                return _success_json(name, out_type, data_string, new_log)

            else:
                out_type, data = build_payload_for_result(
                    result,
                    registry=None,
                    df_rows=20,
                    df_cols=20,
                    include_columns=True,
                    series_max_items=100,
                    ndarray_max_size=1000,
                    ndarray_preview_count=100,
                    list_max_items=100,
                )

            return _success_json(name, out_type, data, new_log)

        except Exception as e:
            return build_error_payload(self, name, e)
    return wrapped


def wrap_main_agent_method(self, name, method):
    def wrapped(**kwargs):
        try:
            previous_log_end = len(self.log.log_text)
            kwargs = prepare_kwargs(self, name, method, kwargs, FILTERER_SET, _resolve_df_value)
            result = method(**kwargs)
            
            self.archive.append(result)
            new_log = self.log.log_text[previous_log_end:]
            new_log = _scrub_log(new_log)

            # Resolve your handle → real object (unchanged)
            if isinstance(result, dict) and "subset_id" in result:
                obj_id = result["subset_id"]
                obj = self.FILTERED_SUMSTATS.get(obj_id)
                result = obj

            # --- If it's a figure/image: SHOW LOCALLY but NEVER return the image ---
            img_payload = image_payload(
                name,
                result,
                new_log,
                _is_figure,
                _show_locally,
                "Image/figure creation finished.",
            )
            if img_payload is not None:
                return img_payload

            ss_payload = sumstats_payload(self, name, result, previous_log_end, FILTERER_SET, _scrub_log)
            if ss_payload is not None:
                return ss_payload

            else:
                out_type, data = build_payload_for_result(
                    result,
                    registry=self.DATA_REGISTRY,
                    df_rows=20,
                    df_cols=40,
                    include_columns=False,
                    series_max_items=100,
                    ndarray_max_size=1000,
                    ndarray_preview_count=100,
                    list_max_items=100,
                )

            return json.dumps({
                "status": "success",
                "method": name,
                "type": out_type,
                "data": data,
                "log": _scrub_log(new_log)
            }, ensure_ascii=False)

        except Exception as e:
            return build_error_payload(self, name, e, scrubber=_scrub_log)
    return wrapped

from dataclasses import dataclass


@dataclass
class DarfixMetadata:
    raw_input_file: str
    raw_detector_data_path: str
    raw_metadata_path: str

    def get_scan_name(self) -> str:
        parts = self.raw_detector_data_path.split("/")
        if len(parts) < 2:
            raise RuntimeError(
                f"Impossible to extract scan name from detector path '{self.raw_detector_data_path}'"
            )
        return parts[1]


def convert_metadata_to_graph_inputs(
    metadata: DarfixMetadata, treated_data_dir: str
) -> list:
    inputs = [dict(name=k, value=v) for k, v in metadata.__dict__.items()]

    inputs.append(dict(name="treated_data_dir", value=treated_data_dir))

    return inputs

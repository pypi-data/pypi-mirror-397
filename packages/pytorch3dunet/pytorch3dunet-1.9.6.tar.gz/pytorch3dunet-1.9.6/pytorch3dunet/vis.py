import h5py
import napari

pred_file1 = "/Users/adrianwolny/workspace/pytorch-3dunet/pytorch3dunet/baseline_ce/train_blob20_predictions.h5"
pred_file3 = "/Users/adrianwolny/workspace/pytorch-3dunet/pytorch3dunet/labels_weight_augs_scale_ce/train_blob20_predictions.h5"
pred_file4 = "/Users/adrianwolny/workspace/pytorch-3dunet/pytorch3dunet/merged_labels_weight_augs_ce/train_blob20_predictions.h5"
raw_file = "/Users/adrianwolny/workspace/pytorch-3dunet/pytorch3dunet/baseline_ce/train_blob20.h5"

with h5py.File(raw_file, "r") as f:
    raw = f["raw"][:]
    label = f["label"][:]

with h5py.File(pred_file1, "r") as f:
    baseline_ce = f["predictions"][:]

with h5py.File(pred_file3, "r") as f:
    merged_labels_weight_ce = f["predictions"][:]

with h5py.File(pred_file4, "r") as f:
    merged_labels_weight_augs_ce = f["predictions"][:]

viewer = napari.Viewer()
viewer.add_image(raw, name="raw")
viewer.add_labels(label, name="label")
viewer.add_labels(baseline_ce, name="baseline_ce")
viewer.add_labels(merged_labels_weight_ce, name="labels_weight_augs_scale_ce")
viewer.add_labels(merged_labels_weight_augs_ce, name="merged_labels_weight_augs_ce")

napari.run()

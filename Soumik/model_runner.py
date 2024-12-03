from model.model_generic import process_abundance_x2


class_l1 = "/tmp/worker_2_34.0_96.6.fits.fits"
background = "model/data/reference/background_allevents.fits"
solar = "data-generated/client/some.txt"
scatter_atable = "data-generated/client/some.fits"

abundance = process_abundance_x2(class_l1, background, solar, scatter_atable, bin_size=2048)
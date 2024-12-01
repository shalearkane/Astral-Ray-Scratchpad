from model.model_generic import process_abundance


class_l1 = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/combined-fits/35.2_85.2.fits"
background = "model/data/reference/background_allevents.fits"
solar = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/flux/some.txt"
scatter_atable = "model/data/reference/tbmodel_20210827T210316000_20210827T210332000.fits"

abundance = process_abundance(class_l1, background, solar, scatter_atable, bin_size=2048)
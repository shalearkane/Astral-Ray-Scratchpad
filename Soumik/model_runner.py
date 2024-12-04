from model.model_handcrafted import process_abundance_h

# from model.model_generic import process_abundance_x2


class_l1 = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class/ch2_cla_l1_20191022T112444865_20191022T112452865.fits"
background = "model/data/reference/background_allevents.fits"
solar = "data-generated/client/some.txt"
scatter_atable = "data-generated/client/some.fits"

# abundance = process_abundance_x2(class_l1, background, solar, scatter_atable, bin_size=2048)
abundance = process_abundance_h(class_l1)
import pprint

pprint.pprint(abundance)

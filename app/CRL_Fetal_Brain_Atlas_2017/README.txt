2017 Fetal Brain Atlas v3
Copyright 2016-2021, Computational Radiology Lab, Boston Childrens Hospital, Boston, MA, 02115

Contact:
fetalmri@crl.med.harvard.edu (please try this address first)
Ali Gholipour: Ali.Gholipour@childrens.harvard.edu
Clemente Velasco-Annis: Clemente.Velasco-Annis@childrens.harvard.edu

This version of the Spatio-Temporal Atlas (STA) was last edited on 02/24/19

This spatio-temporal atlas (fetal brain atlas) and the included parcellations are not intended for medical use and have no warranty. Structures received varying amounts of attention and refinement based on the research goals at the time of creation and thus no guarantees can be made regarding the accuracy or precision of the segmentations, nor the withholding to any particular labeling convention or protocol between structures. Any output derived from the use of these atlases or parcellations shouled be checked in order to validate the accuracy of the results.

# # # # # # # # # # # # # # # # # # # # # #
Update on 02/24/19 - CRL_Fetal_Brain_Atlas_2017v3

Replaced corrupted tissue segmentation file: STA27_tissue.nii.gz

# # # # # # # # # # # # # # # # # # # # # #
Update on 01/08/19 - CRL_Fetal_Brain_Atlas_2017v2

Fixed an error where some segmentations were not correctly gzip'd
("tissue" for STA21-30)

# # # # # # # # # # # # # # # # # # # # # #
New to this update (02/05/18) "Superbowl edition":

This zip is named CRL_Fetal_Brain_Atlas_2017.zip

EXPANDED ATLAS - 36-38:
	The fetal atlas for gestational ages 36-37 have been reconstructed using additional high-quality fetal MRIs
	An all-new week 38 atlas has also been included in the zip
	To differentiate these versions from previous atlas releases, these are named:
		STA36exp.nii.gz
		STA37exp.nii.gz
		STA38exp.nii.gz
	Because these are new atlas images, new "Olympic edition"-protocol segmentations were created for these images

REGIONAL CORTEX PARCELLATION:
	A regional cortex parcellation (which extends into the white matter) has been added alongside the "Olympic edition" segmentations
	These are named:
		STA21_regional.nii.gz
		STA22_regional.nii.gz
		STA23_regional.nii.gz
		STA24_regional.nii.gz
		STA25_regional.nii.gz
		STA26_regional.nii.gz
		STA27_regional.nii.gz
		STA28_regional.nii.gz
		STA29_regional.nii.gz
		STA30_regional.nii.gz
		STA31_regional.nii.gz
		STA32_regional.nii.gz
		STA33_regional.nii.gz
		STA34_regional.nii.gz
		STA35_regional.nii.gz
		STA36exp_regional.nii.gz
		STA37exp_regional.nii.gz
		STA38exp_regional.nii.gz
	The label structure names are noted below, and an ITKsnap label description file has been included as well
	As usual, we give no gaurantees about the accuracy of these labels. In particular for the 'younger' brains, the surface of the brain is much smoother and so there are fewer landmarks to differentiate regions, especially as it comes to regions in the same lobe or group, such as the border between the superior, middle, and inferior occipital gyri
	These labels were warped initially from the ENA33 neonate atlas (citation below) on to our 36-38 atlases. Then the resulting segmentation was propagated down, week-by-week, to the rest of our atlases.
		Citation: Blesa, Manuel, et al. "Parcellation of the healthy neonatal brain into 107 regions using atlas propagation through intermediate time points in childhood." Frontiers in neuroscience 10 (2016): 220.

RENAMED FILES:
	"Olympic edition" segmentations are now named "tissue"
	Note: 21-30 have developing white matter zones/layers, 31-38 don't
	They are now named:
		STA21_tissue.nii.gz
		STA22_tissue.nii.gz
		STA23_tissue.nii.gz
		STA24_tissue.nii.gz
		STA25_tissue.nii.gz
		STA26_tissue.nii.gz
		STA27_tissue.nii.gz
		STA28_tissue.nii.gz
		STA29_tissue.nii.gz
		STA30_tissue.nii.gz
		STA31_tissue.nii.gz
		STA32_tissue.nii.gz
		STA33_tissue.nii.gz
		STA34_tissue.nii.gz
		STA35_tissue.nii.gz
		STA36exp_tissue.nii.gz
		STA37exp_tissue.nii.gz
		STA38exp_tissue.nii.gz	

# # # # # # # # # # # # # # # # # # # # # #
New to this update (11/21/16) "Olympic edition":

CHANGES TO LABELING SCHEME:
	The parcellation scheme (label numbers) has been reorganized
		All atlas images now share the same label key
		The full key can be found below
	Left and right white matter have been separated into separate labels
	Labels for left and right internal capsule have been added to all images
	
REFINEMENT TO PARCELLATIONS:
	"Miscellanous_brain_tissue" has been mostly removed as most of the label was internal capsule
	Developing white matter zones (SP, IZ & VZ) have been removed from STA31-33 because they were not felt to be accurate (differentiation between layers was arbitrary)
		*There are two versions of the STA30 parcellation, one with developing white matter zones, one without*
	Cortical plate was reduced in the region anterior to the corpus callosum (reduced the portion "wrapping" into hemisphere)
	Subplate has been expanded to the appropriate width as per reviewer feedback
	The intermediate zone/ventricular zone has been edited to shrink the ventricular zone in line with reviewer feedback
	Deep gray matter structures have been edited to increase segmentation consistency between gestational ages

# # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # #
New to this update (06/07/16):

	White and gray cerebellum have been recombined because we could not ensure the accuracy of the delineation (very little refinement had been done since initial propagation of the parcellation scheme to this atlas).
	
	The files have been renamed slightly.

# # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # #
New to this update (03/30/16):

ADDED TEMPLATES:
	There are now atlas images and labels for gestational age (GA) weeks 21-37.

DEVELOPING WHITE MATTER ZONES:
	Labels for developing white matter zones have been added for GA 21-33
	This includes left and right "ventricular zone", "intermediate zone" (similar to subventricular zone), and "subplate"
	In these images, label 51 is now "miscellaneous brain tissue", mostly deep gray matter found between the larger subcortical structures

	Note: As the white matter homogenizes in composition during development, the visual differentiation between the layers also decreases. Because of this the accuracy of the developmental layers may not be great for the older brains (i.e. ~STA30). This primarily pertains to the border between intermediate zone and subplate.

ADDITIONAL ADDED LABELS:
	#5: Hippocampal commisure
	#6: Fornix

LABEL REFINEMENTS:
	Many of the labels have been refined to increase accuracy, in particular:
		hippocampus
		caudate
		thalamus
		lentiform
		corpus callosum
		cortical plate
# # # # # # # # # # # # # # # # # # # # # # 

Label key (all images):

    0 Clear Label 
    1 Precentral_L 
    2 Precentral_R 
    3 Frontal_Sup_L 
    4 Frontal_Sup_R 
    5 Frontal_Sup_Orb_L 
    6 Frontal_Sup_Orb_R 
    7 Frontal_Mid_L 
    8 Frontal_Mid_R 
    9 Frontal_Mid_Orb_L 
   10 Frontal_Mid_Orb_R 
   11 Frontal_Inf_Oper_L 
   12 Frontal_Inf_Oper_R 
   13 Frontal_Inf_Tri_L 
   14 Frontal_Inf_Tri_R 
   15 Frontal_Inf_Orb_L 
   16 Frontal_Inf_Orb_R 
   17 Rolandic_Oper_L 
   18 Rolandic_Oper_R 
   19 Supp_Motor_Area_L 
   20 Supp_Motor_Area_R 
   21 Olfactory_L 
   22 Olfactory_R 
   23 Frontal_Sup_Medial_L 
   24 Frontal_Sup_Medial_R 
   25 Frontal_Med_Orb_L 
   26 Frontal_Med_Orb_R 
   27 Rectus_L 
   28 Rectus_R 
   29 Insula_L 
   30 Insula_R 
   31 Cingulum_Ant_L 
   32 Cingulum_Ant_R 
   33 Cingulum_Mid_L 
   34 Cingulum_Mid_R 
   35 Cingulum_Post_L 
   36 Cingulum_Post_R 
   37 Hippocampus_L 
   38 Hippocampus_R 
   39 ParaHippocampal_L 
   40 ParaHippocampal_R 
   41 Amygdala_L 
   42 Amygdala_R 
   43 Calcarine_L 
   44 Calcarine_R 
   45 Cuneus_L 
   46 Cuneus_R 
   47 Lingual_L 
   48 Lingual_R 
   49 Occipital_Sup_L 
   50 Occipital_Sup_R 
   51 Occipital_Mid_L 
   52 Occipital_Mid_R 
   53 Occipital_Inf_L 
   54 Occipital_Inf_R 
   55 Fusiform_L 
   56 Fusiform_R 
   57 Postcentral_L 
   58 Postcentral_R 
   59 Parietal_Sup_L 
   60 Parietal_Sup_R 
   61 Parietal_Inf_L 
   62 Parietal_Inf_R 
   63 SupraMarginal_L 
   64 SupraMarginal_R 
   65 Angular_L 
   66 Angular_R 
   67 Precuneus_L 
   68 Precuneus_R 
   69 Paracentral_Lobule_L 
   70 Paracentral_Lobule_R 
   71 Caudate_L 
   72 Caudate_R 
   73 Putamen_L 
   74 Putamen_R 
   75 Pallidum_L 
   76 Pallidum_R 
   77 Thalamus_L 
   78 Thalamus_R 
   79 Heschl_L 
   80 Heschl_R 
   81 Temporal_Sup_L 
   82 Temporal_Sup_R 
   83 Temporal_Pole_Sup_L 
   84 Temporal_Pole_Sup_R 
   85 Temporal_Mid_L 
   86 Temporal_Mid_R 
   87 Temporal_Pole_Mid_L 
   88 Temporal_Pole_Mid_R 
   89 Temporal_Inf_L 
   90 Temporal_Inf_R 
   91 CorpusCallosum 
   92 Lateral_Ventricle_L 
   93 Lateral_Ventricle_R 
   94 Midbrain_L 
   95 Midbrain_R 
   96 Pons_L 
   97 Pons_R 
   98 Medulla_L 
   99 Medulla_R 
  100 Cerebellum_L 
  101 Cerebellum_R 
  102 Vermis_Ant_L 
  103 Vermis_Ant_R 
  104 Vermis_Post_L 
  105 Vermis_Post_R 
  106 Vermis_Cent_L 
  107 Vermis_Cent_R 
  108 Subthalamic_Nuc_L 
  109 Subthalamic_Nuc_R 
  110 Hippocampal_Comm 
  111 Fornix 
  112 Cortical_Plate_L 
  113 Cortical_Plate_R 
  114 Subplate_L 
  115 Subplate_R 
  116 Inter_Zone_L 
  117 Inter_Zone_R 
  118 Vent_Zone_L 
  119 Vent_Zone_R 
  120 White_Matter_L 
  121 White_Matter_R 
  122 Internal_Capsule_L 
  123 Internal_Capsule_R 
  124 CSF 
  125 misc 

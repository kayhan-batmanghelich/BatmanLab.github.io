#!/usr/bin/env python3
"""
Download all publication images with correct sequential numbering matching HTML.
"""

import json
import urllib.request
from pathlib import Path

def download_image(url, filename):
    """Download image from URL exactly as provided"""
    if not url or url == "":
        return False
    try:
        # Use URL exactly as provided - don't decode/encode it
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                with open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"✓ Downloaded: {filename}")
                return True
            else:
                print(f"✗ HTTP {response.status} for {filename}")
                return False
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP {e.code} for {url[:60]}...")
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__} for {url[:60]}...")
        return False

# Create images directory
images_dir = Path("images/publications")
images_dir.mkdir(parents=True, exist_ok=True)

# Full JSON from user's input
json_data = """{
  "2025": [
    {"title": "A Human-Centered Approach to Identifying Promises, Risks, \\u0026 Challenges of Text-to-Image Generative AI in Radiology", "image_icon_link": ""},
    {"title": "High-dimensional causal mediation analysis by partial sum statistic and sample splitting strategy in imaging genetics application", "image_icon_link": ""},
    {"title": "Performance of Natural Language Processing versus International Classification of Diseases Codes in Building Registries for Patients With Fall Injury: Retrospective Analysis", "image_icon_link": ""},
    {"title": "Multi-Modal Large Language Models are Effective Vision Learners", "image_icon_link": ""}
  ],
  "2024": [
    {"title": "MedSyn: Text-guided Anatomy-aware Synthesis of High-Fidelity 3D CT Images", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.39.24%E2%80%AFPM-600x178.png"},
    {"title": "Mammo-CLIP: A Vision Language Foundation Model to Enhance Data Efficiency and Robustness in Mammography", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.43.25%E2%80%AFPM-600x435.png"},
    {"title": "Anatomy-specific Progression Classification in Chest Radiographs via Weakly Supervised Learning", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.59.40%E2%80%AFPM-600x230.png"}
  ],
  "2023": [
    {"title": "Semi-Implicit Denoising Diffusion Models (SIDDMs)", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-3.47.53%E2%80%AFPM-300x92.png"},
    {"title": "DrasCLR: Self-Supervised Representation Learning via Disentangled Representations and Spectral Clustering", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-2.49.14%E2%80%AFPM-600x467.png"},
    {"title": "Beyond Distribution Shift: Spurious Features Through the Lens of Training Dynamics", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/kmnist_expts-300x161.jpg"},
    {"title": "ComBat Harmonization: Empirical Bayes versus fully Bayes approaches", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-3.12.49%E2%80%AFPM-600x435.png"},
    {"title": "Distilling Blackbox to Interpretable Models for Efficient Transfer Learning", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/Screenshot-2023-10-10-at-11.31.06%E2%80%AFPM-300x159.png"},
    {"title": "Physics-Informed Neural Networks for Tissue Elasticity Reconstruction in Magnetic Resonance Elastography", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/Screenshot-2023-10-10-at-11.45.54%E2%80%AFPM-300x96.png"},
    {"title": "Deep Learning Integration of Chest CT Imaging and Gene Expression Identifies Novel Aspects of COPD", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/06/Screenshot-2023-06-27-at-12.55.23-AM-300x133.png"},
    {"title": "Dividing and Conquering a BlackBox to a Mixture of Interpretable Models: Route, Interpret, Repeat", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/06/Screenshot-2023-06-27-at-12.33.26-AM-300x158.png"},
    {"title": "Augmentation by Counterfactual Explanation — Fixing an Overconfident Classifier", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/11/Screenshot-2022-11-06-at-8.34.02-PM-300x114.png"},
    {"title": "Explaining the Black-box Smoothly – A Counterfactual Approach", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/10/Screen-Shot-2022-10-13-at-12.24.43-AM-283x300.png"}
  ],
  "2022": [
    {"title": "Automated Detection of Premalignant Oral Lesions on Whole Slide Images Using CNN", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/oral-lesions-icon-300x186.png"},
    {"title": "Anatomy-Guided Weakly-Supervised Abnormality Localization in Chest X-rays", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/AGXNet-icon-300x167.png"},
    {"title": "Adversarial Consistency for Single Domain Generalization in Medical Image Segmentation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/adv-consistency-icon-300x167.png"},
    {"title": "Hierarchical Amortized Training for Memory-efficient High-Resolution 3D GAN", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/hierarchical-gan-icon-300x186.png"},
    {"title": "Maximum Spatial Perturbation Consistency for Unpaired Image-to-Image Translation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/max-spatial-perturbation-icon-300x186.png"},
    {"title": "Knowledge Distillation via Constrained Variational Inference", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/05/knowledge-distillation-icon-300x186.png"}
  ],
  "2021": [
    {"title": "Can Contrastive Learning Avoid Shortcut Solutions?", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2021/10/Screen-Shot-2021-10-03-at-8.11.25-PM-300x82.png"},
    {"title": "Deep Learning Prediction of Voxel-Level Liver Stiffness in Patients with Nonalcoholic Fatty Liver Disease", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2021/09/RadAI-300x186.png"},
    {"title": "Self-Supervised Vessel Enhancement Using Flow-Based Consistencies", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2021/07/Rohit-ssl-300x167.png"},
    {"title": "Using Causal Analysis for Conceptual Deep Learning Explanation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2021/07/SumedhaCausalBBX-300x145.png"},
    {"title": "Empowering Variational Inference with Predictive Features: Application to Disease Subtyping", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2021/07/MLHC21-300x133.png"},
    {"title": "Improving Clinical Disease Sub-typing and Future Events Prediction through a Chest CT based Deep Learning Approach", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/12/Screen-Shot-2020-12-29-at-1.13.39-PM-300x154.png"},
    {"title": "Context Matters: Graph-based Self-supervised Representation Learning for Medical Images", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/12/Screen-Shot-2020-12-29-at-12.38.09-PM-300x146.png"}
  ],
  "2020": [
    {"title": "Unpaired Data Empowers Association Tests", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Label-Noise Robust Domain Adaptation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Semi-Supervised Hierarchical Drug Embedding", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "3D-BoxSup: Positive-Unlabeled Learning of Brain Tumor Segmentation Networks From 3D Bounding Boxes", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Human-Machine Collaboration for Medical Image Segmentation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Explanation by Progressive Exaggeration", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Generative-Discriminative Complementary Learning", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"},
    {"title": "Weakly Supervised Disentanglement by Pairwise Similarities", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.52.22-PM-300x146.png"}
  ],
  "2019": [
    {"title": "Geometry-Consistent Adversarial Networks for One-Sided Unsupervised Domain Mapping (GcGAN)", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2019/2019_1-300x158.png"},
    {"title": "Twin Auxiliary Classifiers GAN", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2019/GAN-300x92.png"},
    {"title": "Generative Interpretability: Application in Disease Subtyping", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2019/2019_3_1_r-1-300x186.png"},
    {"title": "Robust Ordinal VAE: Employing Noisy Pairwise Comparisons for Disentanglement", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2019/2019_4_1_r-1.png"}
  ],
  "2018": [
    {"title": "Subject2Vec: Generative-Discriminative Approach from a Set of Image Patches to a Vector", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_1_r-300x135.png"},
    {"title": "A structural equation model for imaging genetics using spatial transcriptomics", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/07/Screen-Shot-2020-07-05-at-7.27.30-PM-300x177.png"},
    {"title": "Causal Generative Domain Adaptation Networks", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_3_r_1-300x122.png"},
    {"title": "Deep Diffeomorphic Normalizing Flows", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_4_r_1.png"},
    {"title": "An Efficient and Provable Approach for Mixture Proportion Estimation Using Linear Independence Assumption", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_5_1_r-300x183.png"},
    {"title": "Deep Ordinal Regression Network for Monocular Depth Estimation", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_6_1_R-300x73.png"},
    {"title": "Textured Graph-Based Model of the Lungs: Application on Tuberculosis Type Classification and Multi-drug Resistance Detection", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2018/2018_7_1_r-300x128.png"}
  ],
  "2017": [
    {"title": "Transformations Based on Continuous Piecewise-Affine Velocity Fields", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2017/2017_1_1_r.png"},
    {"title": "A Likelihood-Free Approach for Characterizing Heterogeneous Diseases in Large-Scale Studies", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2017/2017_2_1_r-300x103.png"}
  ],
  "2016": [
    {"title": "Unsupervised Discovery of Emphysema Subtypes in a Large Clinical Cohort", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2016/2016_1_1_r-300x133.png"},
    {"title": "Probabilistic Modeling of Imaging, Genetics and the Diagnosis", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2016/2016_2_1_r-300x136.png"},
    {"title": "Nonparametric Spherical Topic Modeling with Word Embeddings", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2016/2016_3_1_r.png"},
    {"title": "Inferring Disease Status by non-Parametric Probabilistic Embedding", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2016/2016_4_1_r-300x164.png"}
  ],
  "2015": [
    {"title": "Highly-Expressive Spaces of Well-Behaved Transformations: Keeping It Simple", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2015/2015_1_1_r.png"},
    {"title": "Generative Method to Discover Genetically Driven Image Biomarkers", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2015/2015_2_1_r-300x237.png"}
  ],
  "2014": [
    {"title": "Spherical Topic Models for Imaging Phenotype Discovery in Genetic Studies", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2014/2014_1_1_r.png"},
    {"title": "Diversifying Sparsity Using Variational Determinantal Point Processes", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2014/2014_2_1_r-300x131.png"},
    {"title": "BrainPrint in the Computer-Aided Diagnosis of Alzheimer's Disease", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2014/2014_5_1_r-300x204.png"}
  ],
  "2013": [
    {"title": "Joint Modeling of Imaging and Genetics", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2013/2013_1_1_r-300x164.png"}
  ],
  "2012": [
    {"title": "Dominant Component Analysis of Electro-Physiological Connectivity Network", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2012/2012_1_1_r-300x146.png"},
    {"title": "An integrated Framework for High Angular Resolution Diffusion Imaging-Based Investigation of Structural Connectivity", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2014/2014_4_1_r-300x106.png"},
    {"title": "Generative-Discriminative Basis Learning for Medical Imaging", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2012/2012_3_1-2-300x135.png"}
  ],
  "2011": [
    {"title": "Regularized Tensor Factorization for Multi-Modality Medical Image Classification", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2011/2011_1_1_r-300x136.png"},
    {"title": "Disease Classification and Prediction via Semi-Supervised Dimensionality Reduction", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2011/2011_2_1_r-300x228.png"}
  ],
  "2010": [
    {"title": "Prediction of MCI Conversion via MRI, CSF Biomarkers, and Pattern Classification", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2010/2010_1_1_r-300x220.png"},
    {"title": "Application of Trace-Norm and Low-Rank Matrix Decomposition for Computational Anatomy", "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2010/2010_2_1_r-300x189.png"}
  ]
}"""

data = json.loads(json_data)

# Calculate sequential numbering (HTML uses sequential across all years)
# 2025: 1-4, 2024: 5-7, 2023: 8-17, etc.
seq_num = 1
downloaded = 0
failed = 0
skipped = 0

for year in sorted(data.keys(), reverse=True):
    for pub in data[year]:
        img_url = pub.get("image_icon_link", "")
        if img_url:
            # Determine file extension
            if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                img_filename = f"pub_{year}_{seq_num}.jpg"
            else:
                img_filename = f"pub_{year}_{seq_num}.png"
            
            img_path = images_dir / img_filename
            
            if img_path.exists():
                print(f"⊘ Already exists: {img_filename}")
                skipped += 1
            else:
                if download_image(img_url, str(img_path)):
                    downloaded += 1
                else:
                    failed += 1
        seq_num += 1

print(f"\n{'='*60}")
print(f"Summary: {downloaded} downloaded, {failed} failed, {skipped} skipped")
print(f"{'='*60}")

# Trustworthy AI Lab X GES UCLA Hackathon
# Enhancing CTR Predictions through a Data Clean Room

## Project Overview
This project was developed as part of the Trustworthy AI Lab x GES UCLA Hackathon. The primary goal was to enhance Click-Through Rate (CTR) predictions by securely combining and analyzing data from publishers and advertisers. By utilizing a confidential computing environment and generating synthetic data, we aimed to improve the accuracy and efficiency of ad targeting while ensuring data privacy and compliance with regulations.

## Hackathon Details

### About the Hackathon
The Global Entrepreneurship Society (GES) at UCLA (formerly Three Day Startup) is a highly competitive entrepreneurial education program designed for university students. This year, the GES hosted a hackathon in collaboration with the Trustworthy AI Lab, focusing on generative AI and data collaboration intelligence.

**Hackathon Theme:**
- Utilizing Generative AI to empower “Data Collaboration Intelligence.”
- Developing a Data Clean Room to enhance CTR predictions using privacy-preserving synthetic data.

### Project Prompt
Participants were tasked with creating a secure framework for sharing data between publishers and advertisers, aiming to develop more accurate predictive models for CTR. The project involved integrating heterogeneous data sources, ensuring data privacy, and demonstrating the utility of cross-party data collaboration without direct data exposure.

### Challenges Addressed
1. **Synthetic Data Fidelity:** Creating synthetic datasets that accurately reflect real-world distributions of user behavior data.
2. **Synthetic Data Utility:**
   - **Publishers:** Enhance predictive accuracy for user engagement with news content.
   - **Advertisers:** Refine prediction models for advertisements using synthesized data from news content interactions.

### Dataset Overview
- `train_data_ads.csv`: User demographics, device information, advertisement specifics, and user interaction data.
- `train_data_feeds.csv`: Device info, content engagement metrics, and user interaction labels.

### Expected Outcomes
- Development of accurate predictive models for CTR using anonymized data.
- Effective collaboration within a privacy-preserving environment.
- Enhanced understanding of cross-party data utility.

## Achievements
**Team Name:** DataGuardians
- **1st Place Winner** | Awarded $700 Cash Prize & Internship at Trustworthy AI Lab, UCLA

## Repository Structure
- **DataCleanRoom/**: Contains scripts and documentation related to setting up the data clean room and managing the confidential VM.
- **task 1 - Data Visualization/**: Includes data visualization scripts and outputs.
- **task 2 - Data Cleaning and Model Training/**: Contains data cleaning, feature engineering, and model training scripts.
- **task 3 - Generating Synthetic Data/**: Includes scripts for generating synthetic data.
- **presentation/**: Contains the project presentation files.

## Getting Started
Follow the instructions in each directory to understand the implementation details and how to replicate the results.

### Data Clean Room Setup
This directory contains scripts and instructions for setting up a secure data clean room environment using a confidential VM.

- **decrypt.py**: Script to decrypt encrypted data files.
- **setup_instructions.md**: Step-by-step instructions for setting up the data clean room and managing cryptographic keys.

### Data Visualization (Task 1)
This directory contains scripts and notebooks for visualizing data to identify key insights for enhancing CTR predictions.

- **EDA.ipynb**: Jupyter Notebook for Exploratory Data Analysis.
- **graphing.ipynb**: Jupyter Notebook for creating visualizations.

### Data Cleaning and Model Training (Task 2)
This directory contains scripts and notebooks for cleaning data, engineering features, and training predictive models for CTR.

- **data_cleaning_feature_engineering.ipynb**: Jupyter Notebook for data cleaning and feature engineering.
- **model_training.ipynb**: Jupyter Notebook for training and evaluating predictive models.

### Generating Synthetic Data (Task 3)
This directory contains scripts and notebooks for generating synthetic data to ensure data privacy while maintaining statistical properties necessary for analysis.

- **real_vs_synthetic_analysis.ipynb**: Jupyter Notebook for analyzing real vs. synthetic data.
- **GAN_M4.ipynb**: Jupyter Notebook for the GAN model (version M4).
- **GAN_M9.ipynb**: Jupyter Notebook for the GAN model (version M9).
- **gan_2.ipynb**: Jupyter Notebook for the GAN model (version 2).
- **synthetic_data.csv**: CSV file containing the generated synthetic data.

## Contact
For any questions, please reach out to dts7992@nyu.edu.


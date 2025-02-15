import os
import pandas as pd


def get_gender_attributes(path):
    feat_files = [f for f in os.listdir(path) if f.endswith(".feat")]
    featname_files = [f for f in os.listdir(path) if f.endswith(".featnames")]
    egofeat_files = [f for f in os.listdir(path) if f.endswith(".egofeat")]
    
    node_gender_dict = {} # dictionary to store attributes
    
    for feat_file, featname_file, egofeat_file in zip(feat_files, featname_files, egofeat_files):
        
        # load the data
        features = pd.read_csv(os.path.join(path, feat_file), sep=" ", header=None)
        feature_names = pd.read_csv(os.path.join(path, featname_file), sep=" ", header=None)
        ego_features = pd.read_csv(os.path.join(path, egofeat_file), sep=" ", header=None)

        gender_index = feature_names[feature_names[1] == "gender;anonymized"].index[0]

        # extract gender information
        features = features[[0, gender_index + 1]]
        ego_id = int(egofeat_file.split('.')[0])
        ego_gender = ego_features.iloc[0, gender_index]

        
        features_dict = dict(zip(features[0], features[gender_index + 1]))
        features_dict[ego_id] = ego_gender

        node_gender_dict.update(features_dict)
    
    return node_gender_dict


def save_gender_attributes_to_csv(gender_dict, output_path):
    gender_df = pd.DataFrame(list(gender_dict.items()), columns=['node', 'gender'])
    gender_df.to_csv(output_path, index=False)



localpath = "facebook/"
output_csv = "target.csv"


# extract gender attributes
gender_dict = get_gender_attributes(localpath)

# Save to CSV
save_gender_attributes_to_csv(gender_dict, output_csv)
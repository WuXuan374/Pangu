import os
import tarfile
import logging

'''完成实验结果的打包'''
def my_archive():
    serialization_dir = "predictions/grailqa_1025_original_4500_for_prediction"
    weights = "best.th"
    archive_path = None
    
    weights_file = os.path.join(serialization_dir, weights)
    if not os.path.exists(weights_file):
        logging.error("weights file %s does not exist, unable to archive model", weights_file)
        return

    config_file = os.path.join(serialization_dir, "config.json")
    if not os.path.exists(config_file):
        logging.error("config file %s does not exist, unable to archive model", config_file)
    
    if archive_path is not None:
        archive_file = archive_path
        if os.path.isdir(archive_file):
            archive_file = os.path.join(archive_file, "model.tar.gz")
    else:
        archive_file = os.path.join(serialization_dir, "model.tar.gz")
    logging.info("archiving weights and vocabulary to %s", archive_file)

    with tarfile.open(archive_file, "w:gz") as archive:
        archive.add(config_file, arcname="config.json")
        archive.add(weights_file, arcname="weights.th")
        archive.add(os.path.join(serialization_dir, "vocabulary"), arcname="vocabulary")

if __name__ == '__main__':
    my_archive()
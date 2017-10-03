from os import path
import mass_api_client
from mass_api_client import resources as mass
from mass_api_client.utils import *
import logging
import tempfile
import envoy

logging.basicConfig(level=logging.INFO)

def _get_packer_families(matched_rule_string):
    matched_rule_string = matched_rule_string.lower()
    result = []
    for family in PACKER_FAMILIES:
        if family in matched_rule_string:
            result.append('packerfamily:' + family)
    return result


def upx_unpacker(scheduled_analysis):
    logging.info('Processing {}'.format(str(scheduled_analysis)))
    sample = scheduled_analysis.get_sample()
    with sample.temporary_file() as sample_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            unpacked_file_name = path.join(tmpdir, 'uncompressed_' + path.basename(sample.file_names[0]))
            envoy.run('upx -o {} -d {}'.format(unpacked_file_name, sample_file.name))
            logging.info('Submitting to MASS: {}'.format(unpacked_file_name))
            mass.FileSample.create(unpacked_file_name, open(unpacked_file_name, 'rb'), tags=['decompressed_upx'])
        logging.info('Sending report for {}'.format(str(scheduled_analysis)))
        scheduled_analysis.create_report(additional_metadata={'result': 'uncompressed'})
        

if __name__ == "__main__"   :
    mass_api_client.ConnectionManager().register_connection(
            'default', 
            'IjU5ZDM3Yzc0NmFlY2RmN2MzNGIzYjAyMiI.WhU92Ly9Tq4fc63l0qKfl944Jj4', 
            'http://localhost:8000/api/', 
            timeout=6
            )

    analysis_system_instance = get_or_create_analysis_system_instance(identifier='upxunpacker',
                                                                      verbose_name= 'UPX Unpacker',
                                                                      tag_filter_exp='packerfamily:upx',
                                                                      )
    process_analyses(analysis_system_instance, upx_unpacker, sleep_time=7)

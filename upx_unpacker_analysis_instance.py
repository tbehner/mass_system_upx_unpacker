import os
from os import path
import mass_api_client
from mass_api_client import resources as mass
from mass_api_client.utils import *
import logging
import tempfile
import envoy

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def _get_packer_families(matched_rule_string):
    matched_rule_string = matched_rule_string.lower()
    result = []
    for family in PACKER_FAMILIES:
        if family in matched_rule_string:
            result.append('packerfamily:' + family)
    return result


def upx_unpacker(scheduled_analysis):
    logger.info('Processing {}'.format(str(scheduled_analysis)))
    sample = scheduled_analysis.get_sample()
    with sample.temporary_file() as sample_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            unpacked_file_name = path.join(tmpdir, 'uncompressed_' + path.basename(sample.file_names[0]))
            envoy.run('upx -o {} -d {}'.format(unpacked_file_name, sample_file.name))
            logger.info('Submitting to MASS: {}'.format(unpacked_file_name))
            mass.create_with_file(unpacked_file_name, open(unpacked_file_name, 'rb'), tags=['decompressed_upx'])
        logger.info('Sending report for {}'.format(str(scheduled_analysis)))
        scheduled_analysis.create_report(additional_metadata={'result': 'uncompressed'})
        

if __name__ == "__main__"   :
    api_key = os.getenv('MASS_API_KEY', '')
    logger.info('Got API KEY {}'.format(api_key))
    server_addr = os.getenv('MASS_SERVER', 'http://localhost:8000/api/')
    logger.info('Connecting to {}'.format(server_addr))
    timeout = int(os.getenv('MASS_TIMEOUT', '60'))

    mass_api_client.ConnectionManager().register_connection('default', api_key, server_addr, timeout=timeout)

    analysis_system_instance = get_or_create_analysis_system_instance(identifier='upxunpacker',
                                                                      verbose_name= 'UPX Unpacker',
                                                                      tag_filter_exp='packerfamily:upx',
                                                                      )
    process_analyses(analysis_system_instance, upx_unpacker, sleep_time=7)

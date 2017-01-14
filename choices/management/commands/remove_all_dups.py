from django.core.management.base import BaseCommand, CommandError
from choices.models import Talent, Selection
import os
import sys


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        directory = options['file_path'][1]
        removal_list = self.get_removal_list()
        for talent_list in removal_list:
            i = 0
            for talent in talent_list:
                if i == 0:
                    pass
                else:
                    talent_sample = talent.split('/')[-1]
                    try:
                        talent_object = Talent.objects.get(audio_file=talent_sample)
                        if talent_object and talent_object.selection_set.all().count() > 0:
                            print("deleted: " + talent_object.welo_id)
                            main_talent = Talent.objects.get(audio_file=talent_list[0].split('/')[-1])
                            for selection in talent_object.selection_set.all():
                               try:
                                  new_selection = Selection(talent=main_talent, client=selection.client, status=selection.status)
                                  new_selection.save()
                               except Exception as e:
                                  self.print_error(e)
                                  talent_object.delete()
                            talent_object.delete()
                    except Talent.DoesNotExist:
                        pass
                    except Exception as e:
                        self.print_error(e)

                i += 1

        print(directory)

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    def get_removal_list(self):
        return [
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMEINAS_SAMPLE VOICE_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMEINAS_SAMPLE_ARABIC4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMEINASS_ARABIC_MALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MUBFR-FR_M_2522_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2522_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMCEDRIK_BELGIAN FRENCH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMCEDRIK_FRENCH_FRANCE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMCEDRIK_FRENCH_FRANCE_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMCEDRIK_FRENCH_FRANCE_YOUNG MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002_FR-FR_M_2534.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2534_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2524_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2524_3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_EURO FR MALE5.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEURO FR MALE5.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD EURO FR MALE5.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEST_EURO FR MALE5.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002_FR-FR_M_2521.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2521_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FDA-DK_F_1412_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDA_F_1412_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMREZA_PERSIAN-DARI_SAMPLE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMREZA_PERSIAN-DARI SAMPLE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_SV-SE_F_6113_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFSV-SE_F_6113_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_FR-FR_F_2503_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2503_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002_FR-FR_M_2524.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2524_4.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-DE-DE_F_2930_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDE-DE_F_2930_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_FR-FR_F_2514_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2514_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCS_TAMIL_M_01.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMTAM_MO14.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FDA-DK_F_1411_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDK_F_1411_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MFR-FR_M_2522_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2522_3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-DE-DE_F_2916_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDE-DE_F_2916_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002 HI-IN_F_3414_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHI-IN_F_3414_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-IT-IT_F_3833_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFIT-IT_F_3833_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMIT-IT_M_3811_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-TR-TR_F_6416.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTR-TR_F_6416_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MPT-BR_M_5225_1-2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMPT-BR_M_5225_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PT-BR_F_5209_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPT-BR_F_5209_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_EN-GB_F_1804_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFEN-GB_F_1804_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-FR-CA_F_2710_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-CA_F_2710_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-CA_F_2710_3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002-CN-MA_M_0716.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN-MA_M_0716_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_HU-HU_F_3502_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHU-HU_F_3502_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHU_2002_F_3502.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PT-BR_F_5203_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPT-BR_F_5203_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCS_TAMIL_FE_02.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTAM_F011.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-IT-IT_F_3814_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFIT-IT_F_3814_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_FR-FR_F_2505_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20FUB-FR-FR_F_2505_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2505_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WFNB-NO_F_4715_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNO_F_4715_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FUB-FR-FR_F_2504_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2504_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_GERMAN MALE18.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMGERMAN MALE18.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD GERMAN MALE18.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_2_GERMAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_2_GREECE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PL-PL_F_5011_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPL-PL_F_5011_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAAPL_HUNGARIAN MALE4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD HUNGARIAN MALE4.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_BG-BG_F_0501_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFBG-BG_F_0501_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_FR-FR_F_2504_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2504_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMGERD_INDONESIAN_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMINDONESIAN_MALE_NOYA_DEMO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_HE-IL_F_3313_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHE-IL_F_3313_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MDE_2904_2002.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMDE-DE_M_2904_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PT-BR_F_5204_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPT-BR_F_5204_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_EURO FR MALE3.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEURO FR MALE3.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEST_EURO FR MALE3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/pt-PT_m_5103_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMPT-PT_M_5103_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMKO-KR_M_4113_AHR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMKO-KR_M_4113_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAAPL_HEBREW MALE1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD HEBREW MALE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002_FR-FR_M_2519.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFR-FR_M_2519_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-RU-RU_F_5403_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRU-RU_F_5403_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-ES-LA_F_5922_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFES-LA_F_5922_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMDUTCH MALE2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD DUTCH MALE2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_SK-SK_F_5601_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFSK-SK_F_5601_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-ES-LA_F_5916_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFES-LA_F_5916_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMA. AGUSTA_SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMA. AGUSTA_SPANISH_SOUTH AMERICA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD MANDARIN TW MALE5.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMMANDARIN TW MALE5.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F0702.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF0702_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMKO-KR_M_4114_AHR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMKO-KR_M_4114_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN_M_0719_3.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMCN-M_0719_3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMHERNAN_SPANISH_PUERTO RICO.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMHERNAN_SPANISH_SOUTH AMERICA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCS_TAMIL_FE_03.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTAM_F012.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-RU-RU_F_5406_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRU-RU_F_5406_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJUAN_NEUTRAL_SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJUAN_SPANISH_LATAM.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJUAN_SPANISH_SOUTH AMERICA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-CN-MA_F_0715.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_CN-MA_F_0715_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCN-MA_F_0715_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PT-BR_F_5206_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20FPT-BR_F_5206_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMNICHOLAS_ENGLISH_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMNICHOLAS_ENGLISH_YOUNG_MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJ_JUAN_MEXICAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJ_JUAN_MEXICAN2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_KOREAN MALE 17.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD KOREAN MALE 17.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMKOREAN MALE 17.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMKEVIN_DUTCH_BELGIUM_FLEMISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMTOM_DUTCH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FSL-SL_M_5713_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMSL_M_5713_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_KAREL_FEMALE_UK.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_KAREL_UK.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002_ES_M_5805.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMES-ES_M_5805_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_SK-SK_F_5602_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFSK-SK_F_5602_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFSK_F_5602_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMGT_GERMAN MALE 13.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMGERMAN MALE 13-SEACRH-VIDEO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFEMANUELA_HEBREW_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFEMANUELA_HEBREW_FEMALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_NATIE_PORTUGUESE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_NATIE_PORTUGUESE_BRAZIL.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MVI-VN_M_6815_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFVI-VN_F_6815_1_2002_STUS.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F5916.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF5916_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_JA-JP_F_3903.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFJA-JP_F_3903_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMHU-2002_M_3507.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMHU-HU_M_3507_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMPABLO_NEUTRAL SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMPABLO_SPANISH_SOUTH AMERICA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMHU-HU_M_3508_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMHU_M_3508_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_EL-GR_F_3202_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFEL-GR_F_3202_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WFKO-KR_F_4106_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFKO-KR_F_4106_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-IT-IT_F_3817_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFIT-IT_F_3817_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMAR1A ESPERANZA_MEXICAN_NEUTRAL.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMARIA_ESPERANZA_MEXICAN_NEUTRAL.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCS_TAMIL_FE_01.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTAM_F010.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFTAJIK_ZENNY_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFZENNY_TAJIK_FEMALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-ES-ES_F_5819_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFES-ES_F_5819_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJRN_MIDDLE AGE_FEMALE_KURDISH KURMANJI.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKURDISH_TURKISH_FEMALE VOICE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMIVAN_NEUTRAL_SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMIVAN_SPANISH_LATIN AMERICAN1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F3904.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF3904_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_LIISA_FINNISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_LIISA_FINNISH_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3917_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3917_EMC_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M0708.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN-MA_M_0708_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FPT-PT_F_5108_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPT-PT_F_5108-AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKAREN_ENGLISH_IRELAND_SAMPLE2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKAREN_ENGLISH_UK.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFDIANA_SPANISH_LATAM1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFDIANA_VOICE3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_F_2506.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2506_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_ROSINE_FRENCH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_ROSSINE_ONLINECOURSE_FRENCH_FRANCE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFJA-JP_F_3905_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFJA-JP_F_3905_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKARINA_SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKARINA_SPANISH_LATAM1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFKARINA_SPANISH_PUERTO RICO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMROBERT_CANADIAN ENGLISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMROBERT_CANADIAN_ENGLISH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002-CN-MA_M_0708.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN-MA_M_0708_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_TH-TH_F_6303_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTH-TH_F_6303_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F5203.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF5203_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_RO-RO_F_5315_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRO-RO_F_5315_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-DE-DE_F_2911_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-DE_F_2911_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDE-DE_F_2911_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_CS-CZ_F_1309_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCS-CZ_F_1309_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_CS-CZ_F_1306_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCS-CZ_F_1306_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMALEX_RUSSIAN_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMALEX_RUSSIAN_MALE2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_JUANITA_ENGLISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_JUANITA_ENGLISH_SOUTH_ACCENT.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMAR1A AGUSTA_SPANISH MEXICAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMARIA_AGUSTA_ESPANOL_ECUADOR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFMARIA_AGUSTA_SPANISH_MEXICAN.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFTURKISH FEMALE SAMPLE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFTURKISH FEMALE SAMPLE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_HU-HU_F_3501_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHU-HU_F_3501_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_CN-MA_F_0702.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_CN-MA_F_0702_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F0721.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFCN_MA_F_0721_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMJARNO_TIAIENEN_(M)_FI_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMJARNO_TIAIENEN_(M)_FI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_FR-FR_F_2501_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20FUB-FR-FR_F_2501_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2501_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMEETU_KUNEINEN_(M)_FI_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMEETU_KUNEINEN_(M)_FI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMNICOLAS_VOUTILAINEN_(M)_FI_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMNICOLAS_VOUTILAINEN_(M)_FI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_NATHALIE_BELGIAN FRENCH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJ_NATHALIE_FRENCH_FRANCE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFNATHALIE_FRENCH_FRANCE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MEMC_TM_01.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMEMC_TM_01_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_AR-SA_F_0205_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFAR-SA_F_0205_1_2002.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/pt-PT_m_5101_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMPT-PT_F_5101_AHR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMPT-PT_M_5101_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMRO-RO_M_5304_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMRO_M_5304_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_3_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_3_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M5940.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM_5940_ESLA_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRO-RO_F_5313_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRO_F_5313_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMELMINDARABIC MALE 1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMELMINDARABIC MALE 1_ELM.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD ARABIC MALE 1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMMARTIN1_ENGLISH_CANADA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMMARTIN_USA_ENGLISH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANFKATARZYNA_KASIA_(F)_PL.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WANFKATARZYNA_KASIA_(F)_PL_ANODVAR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCS_TAMIL_M_02.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMTAM_M015.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002-CN-MA_M_0714_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN-MA_M_0714_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMJYRKI_MARKKANEN_(M)_FI_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMJYRKI_MARKKANEN_(M)_FI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJ_THOMAS_FRENCH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJ_THOMAS_FRENCH_FRANCE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMTHOMAS_FRENCH_FRANCE_MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-NL-NL_F_1507_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_NL_F_1507.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNL-NL_F_1507_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3811.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMIT-IT_M_3811_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WFAR-SA_F_0202_1_2002_STUS.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFAR-SA_F_0202_1_2002.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-NL-NL_F_1513_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNL-NL_F_1513_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M2002-IT_M_3801_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMIT-IT_M_3801_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M5805.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM5805_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-NL-NL_F_1506_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNL-NL_F_1506_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F5926.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF5926_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_MANDARIN FEMALE22.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFMANDARIN FEMALE22.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FRU-RU_F_5401_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRU-RU_F_5401_EMC_RU.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEST_EURO SP MALE2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEURO SP MALE2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_VI-VN_F_6803_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20FVI-VN_F_6803_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMVI-VN_M_6815_1_2002_STUS.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-NL-NL_F_1505_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNL-NL_F_1505_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_GERMAN FEMALE13.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFGERMAN FEMALE13.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PT-BR_F_5205_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/W20FPT-BR_F_5205_1-2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPT-BR_F_5205_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3927_5.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3927_5_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_1_GERMAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_1_GREECE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M0716.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN-MA_M_0716_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_ITALIAN MALE2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEST_ITALIAN MALE2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M5901.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMES-LA_M_5901_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_KO-KR_F_4102_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WFKO-KR_F_4102_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFKO-KR_F_4102_AHR.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMWEIWEN_CANTONESE_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMWEIWEN_CHINESE_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMWEIWEN_MANDARIN_MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_KOREAN FEMALE 19.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFKOREAN FEMALE 19.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFVIBECHE_NORWEGIAN_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFVIBECHE_NORWEGIAN_FEMALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2506.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2506_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F3814.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF3814_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMGERMAN MALE 11-SEACRH-VID.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMGT_GERMAN MALE 11.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD GERMAN MALE 11.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3801.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMIT-IT_M_3801_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMWELLINGTON_MEXICAN_SPANISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMWELLINGTON_MEXICAN_SPANISH2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-PL-PL_F_5014_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFPL-PL_F_5014_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFELISABETH_HUNGARIAN_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFELISABETH_HUNGARIAN_FEMALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F3833.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF3833_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCS_TAMIL_M_03.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMTAM_M016.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M5225.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM5225_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002_TR-TR_F_6414_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTR-TR_F_6414_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMHANS_UWE_DIALOGUE (2).mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMHANS_UWE_DIALOGUE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3920.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3920_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFELEANOR_ENGLISH_USA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFELEANOR_TEENAGER_ENGLISH_USA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FTR-TR_F_6409-2002.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFTR-TR_F_6409_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_1_GERMAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_1_GREECE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F5912_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF5912_1_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_1_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_1_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFPATRICIA_DUCTH_BELGIUM.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFPATRICIA_DUTCH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD JAPANESE MALE 18.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMJAPANESE MALE 18.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_2_GERMAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_2_GREECE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAAPL_POLISH MALE 1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD POLISH MALE 1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFGERMAN FEMALE17-SEARCH-VID.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFGT_GERMAN FEMALE17.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F3905_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF3905_1_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-FR_F_2511_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-FR_F_2511_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3918_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3918_EMC_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_MANDARIN FEMALE20.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFMANDARIN FEMALE20.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3921_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3921_EMC_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJAMES_ENGLISH_SCOTTISH_MALE YOUNG VOICE - COPIA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMJAMES_ENGLISH_SCOTTISH_MALE YOUNG VOICE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD LA SPANISH MALE4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMLA SPANISH MALE4.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMHR-TEST.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMKHALED-SAMPLE-2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMARABIC-MALE-KHALED-SAMPLE-2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M3926_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM3926_EMC_JA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANFHELENA_PITKO_(F)_FI_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBFHELENA_PITKO_(F)_FI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MRU-RU_M_5408.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMRU-RU_M_5408_RU_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FVI-VN_F_6808_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFVI-VN_F_6808_1_2OO2_STUS.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FRU-RU_F_5403_EMC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFRU-RU_F_5403_EMC_RU.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMSTEFFAN_ENGLISH UK_MALE YOUNG VOICE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMSTEFFAN_ENGLISH UK_MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MVFCACHE GPO.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMVFCACHE GPO SAMPLE FRENCH_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANFIDA_MARTINSEN_(F)_NO_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBFIDA_MARTINSEN_(F)_NO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMME-AP-ESLA-M.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEST_LA SPANISH MALE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANFJESSICA_PELHAM_(F)_PT_ADNOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WANFJESSICA_PELHAM_(F)_PT_PT.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2503.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOF2503_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F5930.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFES-LA_F_5930_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_JAPANESE MALE1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMJAPANESE MALE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002HI-IN_F_3415_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFHI-IN_F_3415_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJADWIGA_POLISH.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJADWIGA_POLISH_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFJADWIGA_POLISH_FEMALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WD MMASASHI.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMVMWARE_JAPANESE_MASASHI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20M0719.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMCN_MA_M-0719_EMC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WFLV-LV_F_4303_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFLV_F_4303_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFGERMAN FEMALE9-SEARCH-VID.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFGT_GERMAN FEMALE9.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_JAPANESE FEMALE4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFJAPANESE FEMALE4.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMMICHAEL_PANNA_(M)_NO_ANDOVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMMICHAEL_PANNA_(M)_NO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD UK ENGLISH MALE3.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMUK ENGLISH MALE3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFAPPL_EURO FR FEMALE19.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFEURO FR FEMALE19.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WANMESPEN_VERIA _(M)_NO_ANODVAR.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHBMESPEN_VERIA _(M)_NO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_3_GERMAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_3_GREECE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_JAPANESE MALE4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD JAPANESE MALE4.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMJAPANESE MALE4.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_3_ESTONIAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_3_FINNISH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-FR-CA_F_2711_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFFR-CA_F_2711_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MAHR-WUZHILU_MANDARIN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMWUZHI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_2_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_2_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_MANDARIN MALE1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD MANDARIN MALE1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMMANDARIN MALE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAAPL_CZECH MALE7.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD CZECH MALE7.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMDUTCH MALE1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD DUTCH MALE1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20MDE_2906_2002.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMDE-DE_M_2906_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMKEITH_ENGLISH UK__MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMKEITH_ENGLISH UK_MALE_YOUNG VOICE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_3_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_3_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20FAHR-WENDY.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFWEN_SHEN_WENDY.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMPEPE_SPANISH_LATAM.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMPEPE_SPANISH_NEUTRAL.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMPEPE_SPANISH_USA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-NL-NL_F_1519_2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFNL-NL_F_1519_2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_1_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRFF_1_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_2_PORTUGUESE_BRA.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WGRMM_2_SPANISH_LA.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMFADY_ARABIC_MALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMFADY_ARABIC_MALE_BRISTOLTECH.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFEMILIA_BULGARIAN.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFEMILIA_BULGARIAN_FEMALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WF2002_ES-LA_F_5926_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFES-LA_F_5926_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMSTEVE_ENGLISH_SCOTTISH_MALE YOUNG VOICE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRMSTEVE_ENGLISH_SCOTTISH_MALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/W20F2002-DE-DE_F_2913_1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFDE-DE_F_2913_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAPPL_ITALIAN MALE3.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMEST_ITALIAN MALE3.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WATFPT-BR_2MIN_SAMPLE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFLINDA COELLI.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOM2002_ID_MALE_3706.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMID-ID_M_3706_1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFVMWARE JA FEMALE 1.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFVMWARE JAPANESE FEMALE 1.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFVMWARE JA FEMALE 2.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEFVMWARE JAPANESE FEMALE 2.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFYUNXXIA_CANTONESE_FEMALE.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WBRFYUNXXIA_CHINESE_FEMALE.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMAAPL_EURO PT MALE7.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WMEMHD EURO PT MALE7.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMGENERIC DE_MICHAEL HASSINGER.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMWELOCALIZE_GERMAN_MICHAEL.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMSIMPLIFIED_CHINESE_JASON_GENERIC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMVO_DEMO.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMPTBR_EDU OLIVEIRA_GENERIC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMVO EDU OLIVEIRA - WELOCALIZE_GENERIC.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFRANCESCO.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOMFRANCISCO_VENTURA_IT.mp3'
           ],
           [
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFJPN FEMALE_WAKANA_GENERIC.mp3',
              '/Users/william.burton/wevoicerel/media_no_dups/WHOFJPN FEMALE_WAKANA_WELOCALIZE DEMO.mp3'
           ]
        ]

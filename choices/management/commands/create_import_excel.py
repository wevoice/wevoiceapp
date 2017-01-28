from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re
import sys
import xlsxwriter


class Command(BaseCommand):
    help = 'Creates an Excel sheet to be used for import'
    talentdata = []

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+', type=str)

    def print_error(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)

    def create_excel(self):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('Talents.xlsx')
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})

        # Write some data headers.
        worksheet.write('A1', 'audio_file', bold)
        worksheet.write('B1', 'gender', bold)
        worksheet.write('C1', 'code', bold)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0

        # Iterate over the data and write it out row by row.
        for talentfilename, gender, code in self.talentdata:
            worksheet.write(row, col, talentfilename)
            worksheet.write(row, col + 1, gender)
            worksheet.write(row, col + 2, code)
            row += 1

        workbook.close()

    def handle(self, *args, **options):
        filecount = 0
        rejectedcount = 0
        unique = []
        for dirpath, dirnames, filenames in os.walk(unicode(options['file_path'][0], 'utf-8')):
            filenames = [f for f in filenames if not f[0] == '_']
            filenames = [f for f in filenames if not f[0] == '.']
            for filename in filenames:
                if filename not in unique:
                    unique.append(filename)
                    original_filename = filename
                    if " " in filename:
                        newfilename = filename.replace(" ", "")
                        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, newfilename))
                        filename = newfilename
                        original_filename = newfilename
                    if len(filename.split('.')) > 1 and filename.split('.')[-1] in settings.VALID_SOUND_FORMATS:
                        filename_parts = filename.split('.')
                        filename = filename_parts[-2]
                        filetype = filename_parts[-1]
                        if re.match(r'^[A-Za-z]{2}[-|_][A-Za-z]{2}_', filename):
                            if not re.match(r'^[a-z]{2}-[A-Z]{2}_', filename):
                                newfilename = "%s-%s%s.%s" \
                                              % (filename[0:2].lower(), filename[3:5].upper(), filename[5:], filetype)
                                os.rename(os.path.join(dirpath, "%s.%s"
                                                       % (filename, filetype)), os.path.join(dirpath, newfilename))
                                filename = newfilename
                                original_filename = newfilename
                            try:
                                language = re.match(r'^[a-z]{2}-[A-Z]{2}', filename).group()
                                if len(filename.split(language)) > 0:
                                    remainder = re.split(r'(_m_|_f_|_M_|_F_|_u_)', filename.split(language)[1])
                                    if len(remainder) > 1:
                                        gender = remainder[1].strip('_').upper()
                                        self.talentdata.append([original_filename, gender, language])
                                        filecount += 1
                                    else:
                                        print("rejected: %s" % original_filename)
                                        os.remove(os.path.join(dirpath, original_filename))
                                        rejectedcount += 1
                                else:
                                    print("rejected: %s" % original_filename)
                                    os.remove(os.path.join(dirpath, original_filename))
                                    rejectedcount += 1
                            except Exception as file_error:
                                self.print_error(file_error)
                                return '0'
                        else:
                            print("rejected: %s" % original_filename)
                            os.remove(os.path.join(dirpath, original_filename))
                            rejectedcount += 1
                    else:
                        print("removed: %s" % original_filename)
                        os.remove(os.path.join(dirpath, original_filename))
                else:
                    print("duplicate: %s" % filename)
                    os.remove(os.path.join(dirpath, filename))
                    rejectedcount += 1

        self.create_excel()
        self.stdout.write(self.style.SUCCESS('Processed %s. Accepted: %s. Rejected: %s'
                                             % (options['file_path'], filecount, rejectedcount)))

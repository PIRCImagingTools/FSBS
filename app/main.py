import os, sys
import argparse
import utils.helper_functions as helper
import traceback
import registration.registration as reg
import utils.extract_volumes as ev


class MyParser(argparse.ArgumentParser):
    # Purpose of extending ArgumentParser class is to redefine how parser acts on erros
    # now will print out the parser help message
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def build_parser():
    prog_name = 'Fetal Structural Brain Segmentation (FSBS)'
    description = 'Segment subject structural T2 brain MRIs using the Gholipour Atlas.'
    main_prog = 'FSBS'
    version = '1.0'
    usage = f'{main_prog} {{batch_dir/batch_csv/single}} [OPTIONS]'

    #parser = argparse.ArgumentParser(prog = prog_name, description = description, usage = usage)
    parser = MyParser(prog = prog_name, description = description, usage = usage)
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {version}')
    batch_description = "sinlge, batch_dir, or batch_csv"
    subparser = parser.add_subparsers(description = batch_description, dest = 'method', help = 'Registration Methods')

    # Batch Dir parser setup
    dir_parser = subparser.add_parser(name = 'batch_dir', usage = f'{main_prog} batch_dir [OPTIONS]', help = 'Run batch mode using the directory method')
    
    dir_parser.add_argument('directory', 
        help = 'Relative path to perform batch segmentation in.')
    dir_parser.add_argument('ga_excel_path', 
        help = 'Relative path to excel file container GA information.')
    dir_parser.add_argument('-sd', '--search_dir', 
        help = 'Specify directory name in which files must be under', default = None)
    dir_parser.add_argument('-ed', '--exclude_dir', 
        help = 'Specify directory name in which files will be ignored.', default = None)
    dir_parser.add_argument('-st', '--search_term', 
        help = 'Specify reconstruction term that must be in the name of the reconstruction file.', default = 'recon')
    dir_parser.add_argument('-et', '--exclude_term', 
        help = 'Specify reconstruction term that will be ignored.', default = None)
    dir_parser.add_argument('-dr', '--dry_run', 
        help = 'Print number of subjects and any errors and exit without running segmentation.', 
        default = False, action = 'store_true')
    dir_parser.add_argument('--test', default = False, action="store_true", help = argparse.SUPPRESS) # For testing
    dir_parser.add_argument('--repeat', default = False, action="store_true", help = argparse.SUPPRESS) # For testing
    
    # Batch CSV parser setup
    csv_parser = subparser.add_parser(name = 'batch_csv', usage = f'{main_prog} batch_csv [OPTIONS]',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help = 'Run batch mode using the CSV method, will also accept an Excel file.')

    csv_parser.add_argument('csv_file', help = 'Relative path to file to perform batch segmentation on.')
    csv_parser.add_argument('-sl','--subject_label',help = "Column label for Subject IDs", default = 'subject_deid')
    csv_parser.add_argument('-gl','--ga_label',help = "Column label for Subject GAs", default = 'pma')
    csv_parser.add_argument('-rl', '--recon_label',help = "Column label for Recon files", default = 'recon_file')
    csv_parser.add_argument('-ml','--mask_label',help = "Column label for Mask files", default = 'mask_file')
    csv_parser.add_argument('-dr', '--dry_run', 
        help = 'Print number of subjects and any errors and exit without running segmentation.', 
        default = False, action = 'store_true')
    csv_parser.add_argument('--test', default = False, action="store_true", help = argparse.SUPPRESS) # For testing
    csv_parser.add_argument('--repeat', default = False, action="store_true", help = argparse.SUPPRESS) # For testing

    # Single parser setup
    single_parser = subparser.add_parser(name = 'single', usage = f'{main_prog} single [OPTIONS]',
        help = 'Run a single registration call')

    single_parser.add_argument('name', help = 'Subject DEID')
    single_parser.add_argument('gestational_age', help = 'Subject GA in weeks')
    single_parser.add_argument('recon_file', help = 'Path to the Reconstruced Fetal MRI')
    single_parser.add_argument('mask_file', help = 'Path to mask file')
    single_parser.add_argument('--test', default = False, action="store_true", help = argparse.SUPPRESS) # For testing
    single_parser.add_argument('--repeat', default = False, action="store_true", help = argparse.SUPPRESS) # For testing
    
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.method == 'single':
        recon_path = os.path.abspath(os.path.join('/data', args.recon_file))
        mask_path = os.path.abspath(os.path.join('/data', args.mask_file))
        reg.registration(args.name, args.gestational_age, recon_path, mask_path, test_parameters=args.test, repeat=args.repeat)

    elif args.method == 'batch_dir':
        batch_dir = os.path.abspath(os.path.join('/data', args.directory))
        inputs_file = os.path.abspath(os.path.join('/data', args.ga_excel_path))
        reg.batch_registration_dir(batch_dir, inputs_file, 
            search_term = args.search_term, 
            exclude_term = args.exclude_term, 
            search_dir = args.search_dir,
            exclude_dir = args.exclude_dir, 
            dry_run = args.dry_run, 
            test_parameters = args.test, 
            repeat = args.repeat)

    elif args.method == 'batch_csv':
        reg.batch_registration_csv(
            os.path.abspath(os.path.join('/data', args.csv_file)),
            subject_label = args.subject_label, 
            ga_label = args.ga_label, 
            recon_label = args.recon_label, 
            mask_label = args.mask_label, 
            dry_run = args.dry_run,
            test_parameters = args.test,
            repeat = args.repeat)


    elif args.method is None:
        parser.print_help()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\tReceived Keyboard Interrupt, ending program.\n")
        sys.exit(2)

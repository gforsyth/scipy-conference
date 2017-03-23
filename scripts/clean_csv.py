import sys
import subprocess

def fix_domain(fname, replacements):
    """Rename domains that have commas in the name of the domain using ``sed`` in
    subprocess. This is a terrible way to do this, but it works.

    replacements is dictionary where key-val == orig_val: new_val

    """
    for key, val in replacements.items():
        cmd = ['sed', '-i', f's/{key}/{val}/g', fname]
        print(cmd)

        try:
            subprocess.run(cmd)
        except subprocess.CalledProcessError:
            raise subprocess.CalledProcessError("Get a real computer")

reviewer_replacements = {'Earth, Ocean or Geo Science': 'earth',
                         'Biology, Biophysics and Biostatistics': 'bio'}

submission_replacements = {
    'Mini Symposium: ': '',
    'Mini Symposium : ': '',
    'Mini Symposium: ': '', # yes this is necessary
    'Machine Learning and AI': 'Machine Learning and Artificial Intelligence',
    'Computational Science and Numerical Techniques': 'Computational Science',
    'General Track': 'General',
    'Open Data and Reproducibility': 'Reproducibility',
    'Biology, Biophysics and Biostatistics': 'bio',
    'Earth, Ocean and Geosciences': 'earth',
    'Materials Science and Engineering': 'Materials Science',
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""Usage:
        python clean_csv.py csv_file ['reviewer' | 'submission']""")
        sys.exit()
    csv_file = sys.argv[1]
    if sys.argv[2] == 'reviewer':
        fix_domain(csv_file, reviewer_replacements)
    elif sys.argv[2] == 'submission':
        fix_domain(csv_file, submission_replacements)
    else:
        sys.exit('Ummm what?')

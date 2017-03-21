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
    fix_domain('reviewers.csv', reviewer_replacements)
    fix_domain('submissions.csv', submission_replacements)

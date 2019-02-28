# Installing / running scripts

As of now, running anything in the various scripts subdirs assumes that you are
running those scripts from this base directory and you have set `$PYTHONPATH=.`

This is less than ideal, but functional.

## Input files

* conference data excel file (make sure you download this as a "track
  chair", not as a "super chair" since this changes the contents of the
file)
* `reviewers.csv` - from the "Assignment -> Download in CSV" menu option
  (note that the "Assignment" tab won't be visible unless "Assign papers
to program committee" is enabled in the configuration)
* CSV file of volunteer reviewers, should include name, email and list
  of domains they will review in

Put these file names in a config file in the `config` directory to load them correctly.

## Things to check / clean

Reviewer signups -- load in easy chair registrants and the google sheet
of reviewers and do a quick cross check of names / emails.  Volunteers
sometimes use one email to register with one system and another email
with another system.  Prefer the easychair email since we know they
check that one.

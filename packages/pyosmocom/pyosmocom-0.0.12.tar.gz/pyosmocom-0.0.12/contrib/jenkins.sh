#!/bin/sh -xe
# jenkins build helper script.  This is how we build on jenkins.osmocom.org
#
# environment variables:
# * WITH_MANUALS: build manual PDFs if set to "1"
# * PUBLISH: upload manuals after building if set to "1" (ignored without WITH_MANUALS = "1")
# * JOB_TYPE: one of 'test', 'distcheck', 'pylint', 'docs'
#

export PYTHONUNBUFFERED=1

osmo-clean-workspace.sh

case "$JOB_TYPE" in
"test")
	virtualenv -p python3 venv --system-site-packages
	. venv/bin/activate

	pip install -r requirements.txt

	# Execute automatically discovered unit tests
	(cd src && python -m unittest discover -v -s ../tests/)
	;;

"distcheck")
	virtualenv -p python3 venv --system-site-packages
	. venv/bin/activate

	pip install .

	# FIXME: check running any executable programs, if we ever get any
	;;

"pylint")
	# Print pylint version
	pip3 freeze | grep pylint
	# Run pylint to find potential errors
	python3 -m pylint -j0 --errors-only \
		--enable W0301 \
		src tests/*.py
	;;

"docs")
	rm -rf docs/_build
	make -C "docs" html latexpdf

	if [ "$WITH_MANUALS" = "1" ] && [ "$PUBLISH" = "1" ]; then
		make -C "docs" publish publish-html
	fi
	;;
"pysim")
	# Run the pysim tests with pyosmocom from this tree (OS#6570)
	virtualenv -p python3 venv --system-site-packages
	. venv/bin/activate
	pip install . --force-reinstall
	deactivate

	# Clone pysim and remove pyosmocom from requirements.txt, we want to
	# use the version that was just installed into the venv instead
	rm -rf pysim
	git clone https://gerrit.osmocom.org/pysim --depth=1 --branch=master
	cd pysim
	sed -i '/^pyosmocom>=.*/d' requirements.txt
	if grep -q pyosmocom requirements.txt; then
		cat requirements.txt
		set +x
		echo "ERROR: failed to remove pyosmocom from pysim's requirements.txt"
		exit 1
	fi

	# Let pysim enter the same venv and run the tests
	ln -s ../venv .
	SKIP_CLEAN_WORKSPACE=1 JOB_TYPE="test" contrib/jenkins.sh
	;;
*)
	set +x
	echo "ERROR: JOB_TYPE has unexpected value '$JOB_TYPE'."
	exit 1
esac

osmo-clean-workspace.sh

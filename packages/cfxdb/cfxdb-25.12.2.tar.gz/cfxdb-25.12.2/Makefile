# input .fbs files for schema
FBS_FILES=./cfxdb/*.fbs
FBS_OUTPUT=./cfxdb/gen

#FLATC=${HOME}/scm/3rdparty/flatbuffers/flatc
FLATC=/usr/local/bin/flatc

build_flatc:
	cd /tmp && \
	wget https://github.com/google/flatbuffers/archive/v23.5.26.tar.gz && \
	tar xvf v23.5.26.tar.gz && \
	cd flatbuffers-23.5.26 && \
	cmake . && \
	make && \
	sudo cp ./flatc $(FLATC) && \
	cd .. && \
	rm -rf flatbuffers-23.5.26 && rm v23.5.26.tar.gz
	which flatc
	flatc --version

clean:
	-find . -type d -name "__pycache__" -exec rm -rf {} \;
	-rm -rf ./.pytest_cache
	-rm -rf ./.mypy_cache/
	-rm -rf ./build
	-rm -rf ./dist
	-rm -rf ./*.egg-info
	-rm -rf ./.tox

fix_fx_strings:
	find . -type f -exec sed -i 's/Copyright (c) typedef int GmbH. Licensed under MIT./Copyright (c) typedef int GmbH. Licensed under MIT./g' {} \;
	find . -type f -exec sed -i 's/Crossbar.io Database/Crossbar.io Database/g' {} \;

install:
	pip install -e .

publish: clean
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*


stats:
	@echo
	@find ./cfxdb -name "*.fbs" -exec grep -Hi "^table" {} \; | cut -d" " -f1,2 | sort
	@echo
	@find ./cfxdb -name "*.fbs" -exec grep -Hi "^enum" {} \; | cut -d" " -f1,2 | sort
	@echo
	@find ./cfxdb -name "*.fbs" -exec grep -Hi "^struct" {} \; | cut -d" " -f1,2 | sort
	@echo
	@wc -l cfxdb/*.fbs
	@echo
	@cloc cfxdb
	@echo

# list all basic table round-trip tests
list_tests:
	find ./cfxdb/tests/test_*.py -exec grep -Hi "def test_.*roundtrip(" {} \;

test:
	pytest -v -s ./cfxdb/tests/

# FIXME - create missing tests:
# pytest -v -s ./cfxdb/tests/xbr/test_token_balance.py::test_token_balance_roundtrip
# pytest -v -s ./cfxdb/tests/xbr/test_block.py::test_block_roundtrip
test_xbr_roundtrip:
	pytest -v -s ./cfxdb/tests/xbr/test_actor.py::test_actor_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_api.py::test_api_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_catalog.py::test_catalog_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_channel.py::test_channel_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_channel_balance.py::test_channel_balance_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_consent.py::test_consent_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_market.py::test_market_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_member.py::test_member_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_offer.py::test_offer_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_token_approval.py::test_token_approval_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_token_transfer.py::test_token_transfer_roundtrip
	pytest -v -s ./cfxdb/tests/xbr/test_transaction.py::test_transaction_roundtrip

test_single:
	pytest -v -s ./cfxdb/tests/test_user.py::test_user_fbs_roundtrip

test_cookiestore:
	pytest -v -s ./cfxdb/tests/cookiestore/test_cookie.py

test_realmstore:
	pytest -v -s ./cfxdb/tests/realmstore/test_session.py

# auto-format code - WARNING: this my change files, in-place!
# use "pip install yapf==0.29.0"
autoformat:
	yapf -ri --style=yapf.ini \
		--exclude="cfxdb/gen/*" \
		cfxdb

# flatbuffer schema processing / binding code generation
flatc_version:
	$(FLATC) --version

clean_fbs:
	rm -rf $(FBS_OUTPUT)
	mkdir -p $(FBS_OUTPUT)

build_fbs: build_fbs_bfbs build_fbs_python fix_fbs_python

# generate schema type library (.bfbs binary) from schema files
build_fbs_bfbs:
	$(FLATC) -o $(FBS_OUTPUT) --binary --schema --bfbs-comments --bfbs-builtins $(FBS_FILES)

# generate python3 bindings from schema files
build_fbs_python:
	$(FLATC) -o $(FBS_OUTPUT) --python $(FBS_FILES)

fix_fbs_python:
	# those are not generated, but required
	find $(FBS_OUTPUT) -type d -exec touch {}/__init__.py \;

	# FIXME: wrong import:
	# "from oid_t import oid_t" => "from ..oid_t import oid_t"
	find $(FBS_OUTPUT) -name "*.py" -exec sed -i'' 's/from oid_t/from ..oid_t/g' {} \;

build_docs:
	cd ./docs/ && sphinx-build -b html . _build

test_docs:
	cd ./docs/ && sphinx-build -nWT -b spelling -d _build/doctrees . _build/spelling
	cd ./docs/ && sphinx-build -nWT -b dummy . _build

run_docs:
	twistd --nodaemon web --path=./docs/_build --listen=tcp:8091

clean_docs:
	-rm -rf ./docs/_build

fix_copyright:
	find . -type f -exec sed -i 's/Copyright (c) Crossbar.io Technologies GmbH/Copyright (c) typedef int GmbH/g' {} \;

wheel = `ls dist/ | grep -i .whl`

all: clean uninstall build install

clean:
	rm -rf build/ dist/ .eggs

build:
	python setup.py sdist bdist_wheel

uninstall:
	pip uninstall qatlibrary -y

install:
	pip install dist/$(wheel)

reinstall: uninstall install

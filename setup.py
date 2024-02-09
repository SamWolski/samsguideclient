import setuptools

## Dependencies
_requires = [ r for r in
			  open('requirements.txt', 'r', encoding='utf-8')\
			  .read().split('\n') if len(r)>1 ]

setuptools.setup(
	name="SamsGuideClient",
	version="0.0.2",
	description="Sam's Guide Client for the MeasurementEventManager system",
	author="Sam Wolski",
	python_requires=">=3.10",
	packages=["samsguideclient"],
	install_requires=_requires,
	entry_points={
		"console_scripts": [
			"sgc = samsguideclient.cmdline:launch_client",
		],
	},
)

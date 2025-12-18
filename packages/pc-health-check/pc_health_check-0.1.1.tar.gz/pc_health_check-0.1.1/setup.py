from setuptools import setup, find_packages

setup(
    name='pc_health_check',
    version='0.1.1',
    packages=find_packages(exclude=['Servidor', 'Servidor.*']),
    install_requires=[
        'psutil',
        'colorama',
        'websockets'
    ],
    entry_points={
        'console_scripts': [
            'ejemplo = ejemplo.main:main',
            'ejemplo-tunnel = ejemplo.remote_tunnel:start_tunnel',
        ],
    },
    # --- [Informacion EN METADATOS] ---
    description='Herramienta de monitorización de recursos de su equipo PC, Gratis.',
    long_description='Este software es Gratis',
    license='MIT',
    keywords=['sistema', 'recursos', 'gratis', 'libre', 'seguro'],
)
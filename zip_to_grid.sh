rm dbs.zip bins.zip
zip -r dbs.zip ./DBs/Dataset-Muaz/
zip -r bins.zip ./Binaries/Dataset-Muaz/
scp dbs.zip bins.zip gsauger@access.grid5000.fr:nancy/

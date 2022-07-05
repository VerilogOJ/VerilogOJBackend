#!/bin/bash
source `pwd`/../.env

BACKUP_SUFFIX="$1"

if [ -f "backup-files-volume-${BACKUP_SUFFIX}.tar" ] && [ -f "backup-db-${BACKUP_SUFFIX}.sql" ]; then
    docker run -it --rm --name "VLab-Restore-Files" -v "$(pwd):/backup" -v verilog-oj_files-volume:/volume ubuntu:20.04 tar xvf "/backup/backup-files-volume-${BACKUP_SUFFIX}.tar" -C /

    #docker run -it --rm --name "VLab-Restore-DB" -v "$(pwd):/backup" -v verilog-oj_db-volume:/volume ubuntu:20.04 bash -c "rm -rf /volume/*; tar xvf /backup/backup-db-volume-${BACKUP_SUFFIX}.tar -C /volume;"
    cat "backup-db-${BACKUP_SUFFIX}.sql" | docker exec -i verilog-oj-db-1 /usr/bin/mysql -u root --password=${mysql_root_password} django_db
else
    echo "Suffix ${BACKUP_SUFFIX} not present"
    exit 1
fi

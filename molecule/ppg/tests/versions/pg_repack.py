pg_repack_focal_bin_ver = "/usr/lib/postgresql/12/bin/pg_repack: ELF 64-bit LSB shared object," \
                          " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2," \
                          " BuildID[sha1]=d66e27c535df3c13d7594ef715e16fc588285576, for GNU/Linux 3.2.0, stripped"

pgrepack = {"ppg-11.5": {"version": "1.4.4",
                         "binary_version": "pg_repack 1.4.4",
                         "binary": {"centos": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                              " version 1 (SYSV), dynamically linked (uses shared libs),"
                                              " for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=b76f53a7d4ffe7dfab0d9bd5868e99bdfcfe48e9, not stripped",
                                    "ubuntu": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=79aca6e4d94f971b1adc16c4d523ce69a85ad1d4, stripped",
                                    "debian": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked,interpreter"
                                              " /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=9aef45d1e9a16645857aba84473dd8f150998d90, stripped",
                                    "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked,"
                                              " interpreter /lib64/ld-linux-x86-64.so.2,for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=0f89ea7cb7dcbe4435aefd2c74be0505a818614b, stripped",
                                    "rhel": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                            " version 1 (SYSV), dynamically linked,"
                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                            " for GNU/Linux 3.2.0,"
                                            " BuildID[sha1]=a43932c618eeeca37607301c219935b23e13f498, not stripped"}},
            "ppg-11.6": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                                    "binary": {"centos": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable,"
                                                         " x86-64, version 1 (SYSV),"
                                                         " dynamically linked (uses shared libs), for GNU/Linux 2.6.32,"
                                                         " BuildID[sha1]=bd2f6cc2747db832da8302ce8ceaddd6cf56dad0,"
                                                         " not stripped",
                                               "ubuntu": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                         " ELF 64-bit LSB shared object, x86-64,"
                                                         " version 1 (SYSV), dynamically linked,"
                                                         " interpreter /lib64/l,"
                                                         " for GNU/Linux 3.2.0,"
                                                         " BuildID[sha1]=6354cb6b54e6c7c114eafbb054307cd9880a08e4,"
                                                         " stripped",
                                               "debian": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                         " ELF 64-bit LSB shared object, x86-64,"
                                                         " version 1 (SYSV), dynamically linked,"
                                                         " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                         " for GNU/Linux 3.2.0,"
                                                         " BuildID[sha1]=51ee777d6a32be840cd12e7c826a05f4af6e709a,"
                                                         " stripped",
                                               "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack:"
                                                            " ELF 64-bit LSB shared object, x86-64,"
                                                            " version 1 (SYSV), dynamically linked,"
                                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                            " for GNU/Linux 2.6.32,"
                                                            " BuildID[sha1]=882af5eb384bd255a2258bf842d9ec61c0c247dd,"
                                                            " stripped",
                                               "rhel": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable,"
                                                       " x86-64, version 1 (SYSV), dynamically linked,"
                                                       " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                       " for GNU/Linux 3.2.0,"
                                                       " BuildID[sha1]=7b5826a6fdafe64e13a0d0c3192f5b96b8870f6c,"
                                                       " not stripped"}},
            "ppg-11.7": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                         "binary": {"centos": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable,"
                                              " x86-64, version 1 (SYSV), dynamically linked (uses shared libs),"
                                              " for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=18dc799e14ca27086d8b8f33d762e58adee39a7b, not stripped",
                                    "ubuntu": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=cc1e038f5a94c4852724cf889a9335a3aaec58ff, stripped",
                                    "debian": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                              " x86-64, version 1 (SYSV), dynamically linked,"
                                              " interpreter /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=3d33202abb7b689e62f03d7ae4251842b3eaf3c6, stripped",
                                    "debian9.9": "/usr/lib/postgresql/11/bin/pg_repack: ELF 64-bit LSB shared object,"
                                                 " x86-64, version 1 (SYSV), dynamically linked,"
                                                 " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                 " for GNU/Linux 2.6.32,"
                                                 " BuildID[sha1]=cf333e5c432b0341449417e6111fb6ebce20aa9f, stripped",
                                    "rhel": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable,"
                                            " x86-64, version 1 (SYSV), dynamically linked,"
                                            " interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0,"
                                            " BuildID[sha1]=12c0c776186a6f6e6bc44b22921b881c8e5cdc8b, not stripped"}},
            "ppg-11.8": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                         "binary": {"centos": "/usr/pgsql-11/bin/pg_repack:"
                                              " ELF 64-bit LSB executable, x86-64,"
                                              " version 1 (SYSV), dynamically linked (uses shared libs),"
                                              " for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=ec965b02929553830317b07dd4a0048be7e4e772,"
                                              " not stripped",
                                    "ubuntu": "",
                                    "debian": "",
                                    "debian9.9": "/usr/pgsql-11/bin/pg_repack: ELF 64-bit LSB executable, x86-64,"
                                                 " version 1 (SYSV), dynamically linked (uses shared libs),"
                                                 " for GNU/Linux 2.6.32,"
                                                 " BuildID[sha1]=ec965b02929553830317b07dd4a0048be7e4e772,"
                                                 " not stripped",
                                    "rhel": ""}},
            "ppg-12.2": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                         "binary": {"centos": "/usr/pgsql-12/bin/pg_repack: ELF 64-bit LSB executable,"
                                              " x86-64, version 1 (SYSV),"
                                              " dynamically linked (uses shared libs),"
                                              " for GNU/Linux 2.6.32,"
                                              " BuildID[sha1]=23be32801393894d8b6840dce7548ce08aa61cfa,"
                                              " not stripped",
                                    "ubuntu": "/usr/lib/postgresql/12/bin/pg_repack: ELF 64-bit LSB "
                                              "shared object, x86-64, version 1 (SYSV),"
                                              " dynamically linked, interpreter /lib64/l,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=ccb23f9c3eb9b6da117e315e83c6891f8e8499a0,"
                                              " stripped",
                                    "ubuntu-focal": pg_repack_focal_bin_ver,
                                    "debian": "/usr/lib/postgresql/12/bin/pg_repack: ELF 64-bit LSB shared "
                                              "object, x86-64, version 1 (SYSV), dynamically linked,"
                                              " interpreter /lib64/ld-linux-x86-64.so.2,"
                                              " for GNU/Linux 3.2.0,"
                                              " BuildID[sha1]=4bbdde54243ee8f3ce05eae90db2488d543e56ef,"
                                              " stripped",
                                    "debian9.9": "/usr/lib/postgresql/12/bin/pg_repack: ELF 64-bit LSB "
                                                 "shared object, x86-64,"
                                                 " version 1 (SYSV), dynamically linked,"
                                                 " interpreter /lib64/ld-linux-x86-64.so.2, "
                                                 "for GNU/Linux 2.6.32, "
                                                 "BuildID[sha1]=627b47874890b10ec34358f8c8cc82713b28e615,"
                                                 " stripped",
                                    "rhel": "/usr/pgsql-12/bin/pg_repack: ELF 64-bit LSB executable,"
                                            " x86-64, version 1 (SYSV), dynamically linked,"
                                            " interpreter /lib64/ld-linux-x86-64.so.2,"
                                            " for GNU/Linux 3.2.0,"
                                            " BuildID[sha1]=3701679a889dec1d4e53942b80300b9f9064d462,"
                                            " not stripped"}},
            "ppg-12.3": {"version": "1.4.5",
                         "binary_version": "pg_repack 1.4.5",
                         "binary": {"centos": "",
                                    "ubuntu": "",
                                    "ubuntu-focal": pg_repack_focal_bin_ver,
                                    "debian": "",
                                    "debian9.9": "/usr/lib/postgresql/12/bin/pg_repack: ELF 64-bit LSB shared object,"
                                                 " x86-64, version 1 (SYSV),"
                                                 " dynamically linked,"
                                                 " interpreter /lib64/ld-linux-x86-64.so.2,"
                                                 " for GNU/Linux 2.6.32,"
                                                 " BuildID[sha1]=c17dde3971672590d4f56a226115dece9f249784,"
                                                 " stripped",
                                    "rhel": ""}}
            }

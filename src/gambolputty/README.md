Base Classes
==========

#####BaseModule

Base class for all GambolPutty modules that will run not run.
If you happen to override one of the methods defined here, be sure to know what you
are doing ;) You have been warned ;)

    Configuration example:

    - module: SomeModuleName
      alias: AliasModuleName                    # <default: ""; type: string; is: optional>
      configuration:
        work_on_copy: True                      # <default: False; type: boolean; is: optional>
        redis_client: RedisClientName           # <default: ""; type: string; is: optional>
        redis_key: XPathParser%(server_name)s   # <default: ""; type: string; is: required if redis_client is True else optional>
        redis_ttl: 600                          # <default: 60; type: integer; is: optional>
      receivers:
       - ModuleName
       - ModuleAlias

#####BaseThreadedModule

Base class for all GambolPutty modules that will run as separate threads.
If you happen to override one of the methods defined here, be sure to know what you
are doing ;) You have been warned ;)

Running a module as a thread should only be done if the task is mainly I/O bound or the
used python code will release the GIL during its man work.
Otherwise a threaded module is prone to slow everything down.

    Configuration example:

    - module: SomeModuleName
      alias: AliasModuleName                    # <default: ""; type: string; is: optional>
      pool_size: 4                              # <default: 1; type: integer; is: optional>
      configuration:
        work_on_copy: True                      # <default: False; type: boolean; is: optional>
        redis_client: RedisClientName           # <default: ""; type: string; is: optional>
        redis_key: XPathParser%(server_name)s   # <default: ""; type: string; is: required if redis_client is True else optional>
        redis_ttl: 600                          # <default: 60; type: integer; is: optional>
      receivers:
       - ModuleName
       - ModuleAlias

#####BaseMultiProcessModule

Base class for all GambolPutty modules that will run as separate processes.
If you happen to override one of the methods defined here, be sure to know what you
are doing ;) You have been warned ;)

Running a module as its own process solves GIL related problems and allows to utilize more
than just a single core on a multicore machine.
But this comes with some (not so small) drawbacks. Passing data to and from a process
involves pickling/unpickling. This results in a major overhead compared to normal queues
in a threaded environment.

    Configuration example:

    - module: SomeModuleName
      alias: AliasModuleName                    # <default: ""; type: string; is: optional>
      pool_size: 4                              # <default: 1; type: integer; is: optional>
      configuration:
        work_on_copy: True                      # <default: False; type: boolean; is: optional>
        redis_client: RedisClientName           # <default: ""; type: string; is: optional>
        redis_key: XPathParser%(server_name)s   # <default: ""; type: string; is: required if redis_client is True else optional>
        redis_ttl: 600                          # <default: 60; type: integer; is: optional>
      receivers:
       - ModuleName
       - ModuleAlias
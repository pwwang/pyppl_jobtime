
pyppl_jobtime
=============

Job running time statistics for `PyPPL <https://github.com/pwwang/PyPPL>`_.

Installation
------------

Require ``R`` and ``ggplot2``.

.. code-block:: shell

   pip install pyppl_jobtime

After this plugin is installed, a file named ``job.time`` will be created in each job directory with running time in seconds saved in it.

Plotting the running time profile
---------------------------------

.. code-block:: shell

   pyppl jobtime --proc pVcfFix --outfile profile.png


.. image:: ./images/profile.png
   :target: ./images/profile.png
   :alt: profile.png



* 
  Using violin plot:

  .. code-block:: shell

       pyppl jobtime --proc pVcfFix --outfile violin.png --plottype violin

    
  .. image:: ./images/violin.png
     :target: ./images/violin.png
     :alt: violin.png


* 
  Changing process names:

  .. code-block:: shell

       pyppl jobtime --outfile procnames.png \
           --proc pVcfFix --ggs.scale_x_discrete:dict \
           --ggs.scale_x_discrete.labels:list A B C

    
  .. image:: ./images/procnames.png
     :target: ./images/procnames.png
     :alt: procnames.png


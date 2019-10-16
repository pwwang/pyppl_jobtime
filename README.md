# pyppl_jobtime

Job running time statistics for [PyPPL](https://github.com/pwwang/PyPPL).

## Installation
Require `R` and `ggplot2`.
```shell
pip install pyppl_jobtime
```

Enable it with `PyPPL`:
- In configuration file:
  ```yaml
  default:
    _plugins:
        - pyppl_jobtime
  # ... other configurations
  ```

Then a file named `job.time` will be created in each job directory with running time in seconds saved in it.

## Plotting the running time profile
```shell
pyppl jobtime -proc pVcfFix -outfile profile.png
```

![profile.png](./images/profile.png)

- Using violin plot:
    ```shell
    pyppl jobtime -proc pVcfFix -outfile violin.png -plottype violin
    ```
    ![violin.png](./images/violin.png)

- Changing process names:
    ```shell
    pyppl jobtime -proc pVcfFix -outfile violin.png -plottype violin
    ```

    ![procnames.png](./images/procnames.png)

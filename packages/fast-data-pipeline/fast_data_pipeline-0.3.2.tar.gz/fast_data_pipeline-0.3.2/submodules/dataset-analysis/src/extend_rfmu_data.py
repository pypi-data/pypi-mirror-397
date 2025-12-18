import polars as pl
import numpy as np

def get_dynamic_wheel_radius(df: pl.DataFrame) -> float:

    df_filt = df.filter(
        (pl.col("is_brake_actuated") < 0.5) & (pl.col("rfmu_velocity_x_mps").abs > 0)
    )

    return (df_filt["rfmu_velocity_x_mps"] / df_filt["measurement_wheel_angular_velocity_actual_radps"]).mean().item()


def extend_rfmu_data(df: pl.DataFrame) -> pl.DataFrame:
    dynamic_wheel_radius = get_dynamic_wheel_radius(df)
    ret = df.with_columns(
        measurement_circumferential_velocity_mps=dynamic_wheel_radius * pl.col("measurement_wheel_angular_velocity_actual_radps"),
        longitudinal_slip=(pl.col("measurement_circumferential_velocity_mps") - pl.col("hi5_velocity_x_mps")) / pl.max_horizontal("measurement_circumferential_velocity_mps", "hi5_velocity_x_mps"),
        friction_coefficient= pl.col("measurement_wheel_force_x_actual_N") /  pl.col("measurement_wheel_force_z_actual_N"),
    )

    return ret

def fit_magic_formula(df: pl.DataFrame):

    from magic_formula_fitting import fit_tire_parameters

    results = fit_tire_parameters(
            force_n=df["friction_coefficient"],
            load_n=np.ones(len(df["friction_coefficient"])),  # Assuming a constant load of 1000 N
            sigma=df["longitudinal_slip"],
            config=FITTING_CONFIG,
            fit_flags=FITTING_CONFIG.fit_flags
        )
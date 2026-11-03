import pandas as pd


def inpatient_census(df, date_ref, date_start, date_end):
    """Effectif journalier de `date_start` à `date_end`.

    Pour chaque jour J (dates normalisées au jour) :
      - initial_inpatient_census : admission_date < J ET discharge_date_prediction >= J
        (les patients qui sortent le jour J sont encore présents en début de journée)
      - new_admissions    : admission_date == J ET label == 0
      - new_readmissions  : admission_date == J ET label == 1
      - inpatient_discharges : discharge_date_prediction == J
      - final_inpatient_census = initial + admissions + réadmissions - sorties

    Avec ces définitions le stock est conservé d'un jour à l'autre :
    initial(J+1) == final(J) (exigence F05).
    """
    admission = df["admission_date"].dt.normalize()
    discharge = df["discharge_date_prediction"].dt.normalize()
    label = df["label"]

    records = []
    for date in pd.date_range(start=date_start, end=date_end, freq="D"):
        initial = int(((admission < date) & (discharge >= date)).sum())
        new_admissions = int(((admission == date) & (label == 0)).sum())
        new_readmissions = int(((admission == date) & (label == 1)).sum())
        discharges = int((discharge == date).sum())

        records.append(
            {
                "date": date,
                "initial_inpatient_census": initial,
                "new_admissions": new_admissions,
                "new_readmissions": new_readmissions,
                "inpatient_discharges": discharges,
                "final_inpatient_census": initial + new_admissions + new_readmissions - discharges,
                "is_forecast": bool(date >= pd.Timestamp(date_ref)),
            }
        )

    df_census = pd.DataFrame(records)
    df_census["date"] = pd.to_datetime(df_census["date"])
    return df_census.sort_values("date").reset_index(drop=True)


def calculate_kpi (
        df_inpatient,
):
    avg_inpatient = df_inpatient["final_inpatient_census"].mean().round(2)
    max_inpatient = df_inpatient["final_inpatient_census"].max()
    min_inpatient = df_inpatient["final_inpatient_census"].min()

    return avg_inpatient, max_inpatient, min_inpatient
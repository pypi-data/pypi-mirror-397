import pandas as pd

def calculate_metrics(df, verbose=False):
    # Υπολογισμός βασικών στατιστικών (Όλο το ιστορικό)
    variance = df['close'].var()
    std_dev  = df['close'].std()
    skewness = df['close'].skew()
    kurtosis = df['close'].kurt()
    
    if verbose:
        print(f"Variance (Διακύμανση): {variance}")
        print(f"StDev (Τυπική Απόκλιση): {std_dev}")
        print(f"Skew (Ασυμμετρία): {skewness}")
        print(f"Kurtosis (Κύρτωση): {kurtosis}")
        
    # Επιστρέφουμε τα αποτελέσματα ως dictionary για εύκολη πρόσβαση
    return {
        "variance": variance,
        "std_dev": std_dev,
        "skewness": skewness,
        "kurtosis": kurtosis,
    }

# Χρήση:
# metrics = calculate_metrics(df, verbose=True)
# print(metrics['std_dev'])
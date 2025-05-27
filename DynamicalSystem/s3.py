import csv
import matplotlib.pyplot as plt
import os
import numpy as np
import sobol_seq
import copy

num_students = 625
time_steps = 20
dt = 1
merged_students = {}

# خواندن ردیف‌های فایل csv
def read_csv_rows(filename, start=0, count=625):
    rows = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i < start:
                continue
            if i >= start + count:
                break
            data = {key: float(value) for key, value in row.items()}
            rows.append(data)
    return rows

# مقداردهی اولیه دانش
def estimate_K0(P, I):
    avg = (P + I) / 2
    if avg < 0.2:
        return 0.1
    elif avg < 0.4:
        return 0.25
    elif avg < 0.6:
        return 0.4
    elif avg < 0.8:
        return 0.6
    else:
        return 0.8
    

# پارامترهای ثابت
fixed_params = {
    'beta_K': 0.08,
    'beta_E': 0.08,
    'gamma_M': 0.1,
    'theta_E': 0.08,
    'delta_K': 0.1,
    'delta_M': 0.1,
    'delta_E': 0.1
}

# محاسبه ماتریس A برای تحلیل پایداری
# بر اساس مدل خطی شده: dx/dt = A * x
# فقط برای تحلیل تئوری - از مقدار پارامترهای متوسط استفاده می‌کنیم
def build_A_matrix(params):
    A = np.zeros((5, 5))
    A[0][0] = -params['delta_K']
    A[0][3] = params['alpha_P']
    A[0][4] = params['alpha_I']
    A[1][0] = params['beta_K']
    A[1][2] = params['beta_E']
    A[1][1] = -params['delta_M']
    A[2][1] = params['gamma_M']
    A[2][2] = -params['delta_E']
    A[3][2] = params['theta_E']
    A[3][3] = -params['delta_P']
    A[4][3] = params['lambda_P']
    A[4][4] = -params['delta_I']
    return A

def apply_events(t, student):
    if t == 5:  # بازخورد معلم
        student["M"][-1] = min(student["M"][-1] + 0.25, 1.0)
        student["E"][-1] = min(student["E"][-1] + 0.25, 1.0)
    elif t == 10:  # آزمون
        student["K"][-1] = min(student["K"][-1] + 0.25, 1.0)
        student["M"][-1] = max(student["M"][-1] - 0.25, 0.0)
    elif t in [7, 14]:  # تکلیف سخت
        student["delta_P"] = min(student.get("delta_P", 0.25) + 0.25, 1.0)
        student["delta_I"] = min(student.get("delta_I", 0.25) + 0.25, 1.0)
    elif t == 15:  # بحث گروهی
        student["I"][-1] = min(student["I"][-1] + 0.25, 1.0)
        student["E"][-1] = min(student["E"][-1] + 0.25, 1.0)

def run_simulation(students, with_events=True):
    for t in range(time_steps):
        for student in students.values():
            if with_events:
                apply_events(t, student)
            
            M, E, P, I, K = student["M"][-1], student["E"][-1], student["P"][-1], student["I"][-1], student["K"][-1]

            dK = student["alpha_P"] * P + student["alpha_I"] * I - student["delta_K"] * K
            dM = student["beta_K"] * K + student["beta_E"] * E - student["delta_M"] * M
            dE = student["gamma_M"] * M - student["delta_E"] * E
            dP = student["theta_E"] * E - student["delta_P"] * P
            dI = student["lambda_P"] * P - student["delta_I"] * I

            student["K"].append(min(max(K + dK * dt, 0), 1))
            student["M"].append(min(max(M + dM * dt, 0), 1))
            student["E"].append(min(max(E + dE * dt, 0), 1))
            student["P"].append(min(max(P + dP * dt, 0), 1))
            student["I"].append(min(max(I + dI * dt, 0), 1))

# مسیر فایل فقط شامل حالت‌های اولیه
state_file = 'C:/Tannaz/Coding-Stuff/AZ/MultiFile/M2/New/parameter_combinations2.csv'
param_file = 'C:/Tannaz/Coding-Stuff/AZ/MultiFile/M2/New/parameter_combinations.csv'

state_data = read_csv_rows(state_file, start=0, count=num_students)
param_data = read_csv_rows(param_file, start=0, count=num_students)
min_len = min(len(state_data), len(param_data))
print(f"شبیه‌سازی برای {min_len} دانش‌آموز آغاز شد.")

# مقدارهای مجاز برای هر پارامتر
param_allowed = {
    'alpha_P': [0.0, 0.25, 0.5],
    'alpha_I': [0.0, 0.25, 0.5],
    'delta_P': [0.0, 0.25, 0.5, 0.75, 1.0],
    'delta_I': [0.0, 0.25, 0.5, 0.75, 1.0],
    'lambda_P': [0.0, 0.25, 0.5, 0.75, 1.0]
}

def map_to_nearest_allowed(val, allowed_values):
    return min(allowed_values, key=lambda x: abs(x - val))

# تولید مقادیر Sobol برای پارامترهای انتخابی
sobol_dim = len(param_allowed)
sobol_vals = sobol_seq.i4_sobol_generate(sobol_dim, num_students)

# ادغام داده‌ها با پارامترهای Sobol
for idx in range(min_len):
    d2 = state_data[idx]  # فقط داده‌های اولیه
    sobol = sobol_vals[idx]

    param_values = {}
    for i, key in enumerate(param_allowed):
        param_values[key] = map_to_nearest_allowed(sobol[i], param_allowed[key])

    merged = {**param_values, **d2}
    merged["id"] = idx + 1

    P = merged["P"]
    I = merged["I"]
    K0 = estimate_K0(P, I)

    merged["K"] = [K0]
    merged["P"] = [P]
    merged["I"] = [I]
    merged["M"] = [merged["M"]]
    merged["E"] = [merged["E"]]
    merged["event_log"] = []

    for key, value in fixed_params.items():
        if key not in merged:
            merged[key] = value

    merged_students[idx + 1] = merged

before_events_students = copy.deepcopy(merged_students)
after_events_students = copy.deepcopy(merged_students)

print("Running simulation without events...")
run_simulation(before_events_students, with_events=False)

print("Running simulation with events...")
run_simulation(after_events_students, with_events=True)

# تحلیل پایداری روی یک نمونه پارامتر (میانگین مقادیر)
mean_params = {k: np.mean([student[k] for student in merged_students.values()]) for k in [
    'alpha_P', 'alpha_I', 'delta_P', 'delta_I', 'lambda_P', 'beta_K', 'beta_E', 'gamma_M', 'theta_E', 'delta_K', 'delta_M', 'delta_E']}
A = build_A_matrix(mean_params)
eigenvalues = np.linalg.eigvals(A)

print("\n🧮 Eigenvalues of A (for stability analysis):")
for i, val in enumerate(eigenvalues):
    print(f"  λ{i+1}: {val.real:.4f} {'+' if val.imag >= 0 else '-'} {abs(val.imag):.4f}j")

# ذخیره لاگ خروجی
log_filename = "students_log.txt"
with open(log_filename, "w", encoding="utf-8") as log_file:
    # تحلیل پایداری - مقادیر eigenvalue
    log_file.write("🧮 Eigenvalues of A (for stability analysis):\n")
    for i, val in enumerate(eigenvalues):
        log_file.write(f"  λ{i+1}: {val.real:.4f} {'+' if val.imag >= 0 else '-'} {abs(val.imag):.4f}j\n")
    log_file.write("\n" + "="*60 + "\n\n")

    log_file.write("📘 Simulation Results:\n\n")
    
    for sid in merged_students.keys():
        s_before = before_events_students[sid]
        s_after = after_events_students[sid]

        log_file.write(f"👤 Student #{sid}\n")
        log_file.write("Initial:\n")
        log_file.write(f"  K: {s_before['K'][0]:.4f}, M: {s_before['M'][0]:.4f}, E: {s_before['E'][0]:.4f}, P: {s_before['P'][0]:.4f}, I: {s_before['I'][0]:.4f}\n")
        log_file.write("Final (No Events):\n")
        log_file.write(f"  K: {s_before['K'][-1]:.4f}, M: {s_before['M'][-1]:.4f}, E: {s_before['E'][-1]:.4f}, P: {s_before['P'][-1]:.4f}, I: {s_before['I'][-1]:.4f}\n")
        log_file.write("Final (With Events):\n")
        log_file.write(f"  K: {s_after['K'][-1]:.4f}, M: {s_after['M'][-1]:.4f}, E: {s_after['E'][-1]:.4f}, P: {s_after['P'][-1]:.4f}, I: {s_after['I'][-1]:.4f}\n")
        log_file.write("Params (Initial):\n")
        log_file.write(f"  alpha_P: {merged_students[sid]['alpha_P']}, alpha_I: {merged_students[sid]['alpha_I']}, delta_P: {merged_students[sid]['delta_P']}, delta_I: {merged_students[sid]['delta_I']}, lambda_P: {merged_students[sid]['lambda_P']}\n")
        log_file.write("Params (Final, No Events):\n")
        log_file.write(f"  alpha_P: {s_before['alpha_P']}, alpha_I: {s_before['alpha_I']}, delta_P: {s_before['delta_P']}, delta_I: {s_before['delta_I']}, lambda_P: {s_before['lambda_P']}\n")
        log_file.write("Params (Final, With Events):\n")
        log_file.write(f"  alpha_P: {s_after['alpha_P']}, alpha_I: {s_after['alpha_I']}, delta_P: {s_after['delta_P']}, delta_I: {s_after['delta_I']}, lambda_P: {s_after['lambda_P']}\n")
        log_file.write("-" * 50 + "\n")

print(f"\n✅ Results saved to '{log_filename}'")

# نمودار میانگین
output_dir = "student_charts"
os.makedirs(output_dir, exist_ok=True)
time_points = list(range(time_steps + 1))

def avg(var, students):
    return [sum(student[var][t] for student in students.values()) / len(students) for t in time_points]

# Plot before events
plt.figure(figsize=(12, 6))
plt.plot(time_points, avg("K", before_events_students), label="Avg K (Knowledge)", linewidth=2)
plt.plot(time_points, avg("M", before_events_students), label="Avg M (Motivation)", linewidth=2)
plt.plot(time_points, avg("E", before_events_students), label="Avg E (Engagement)", linewidth=2)
plt.plot(time_points, avg("P", before_events_students), label="Avg P (Preparedness)", linewidth=2)
plt.plot(time_points, avg("I", before_events_students), label="Avg I (Involvement)", linewidth=2)

plt.title("Average Learning Dynamics Without Events")
plt.xlabel("Time Steps")
plt.ylabel("Average Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("combined_student_dynamics_no_events.png")
plt.close()

# Plot after events
plt.figure(figsize=(12, 6))
plt.plot(time_points, avg("K", after_events_students), label="Avg K (Knowledge)", linewidth=2)
plt.plot(time_points, avg("M", after_events_students), label="Avg M (Motivation)", linewidth=2)
plt.plot(time_points, avg("E", after_events_students), label="Avg E (Engagement)", linewidth=2)
plt.plot(time_points, avg("P", after_events_students), label="Avg P (Preparedness)", linewidth=2)
plt.plot(time_points, avg("I", after_events_students), label="Avg I (Involvement)", linewidth=2)

plt.title("Average Learning Dynamics With Events")
plt.xlabel("Time Steps")
plt.ylabel("Average Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("combined_student_dynamics_with_events.png")
plt.close()

print("✅ Combined average charts saved as 'combined_student_dynamics_no_events.png' and 'combined_student_dynamics_with_events.png'")
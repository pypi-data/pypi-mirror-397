# cRegression

**cRegression** is a fast and easy-to-use Python library for **linear regression**, powered by a **C++ backend** using **pybind11**.  
It allows you to fit simple linear regression models, make predictions, and evaluate model performance efficiently with **NumPy arrays**.

---

**Fast C++ regression library with Python bindings.**

`cRegression` is a high-performance linear regression library written in C++ with seamless Python integration using `pybind11` and `numpy`. It provides a simple API for fitting models and making predictions with the speed of C++.

## Installation

You can install `cRegression` using pip:

```bash
pip install cRegression
```

## Usage


```python
import numpy as np
from cRegression import LinearRegression
```

### 2. Prepare your data

```python
# Example data
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])
```

### 3. Create a LinearRegression object

```python
lr = LinearRegression(x, y)
```

### 4. Access model parameters

```python
print("Slope (b):", lr.slope())
print("Intercept (a):", lr.intercept())
```

### 5. Make predictions

```python
new_x = [6, 7]
predictions = lr.predict(new_x)
print("Predicted y:", predictions)
```

### 6. View detailed regression statistics

```python
lr.summary()
```

This prints a complete summary including:

- Mean(X) and Mean(Y)
- Pearson correlation
- Std(X) and Std(Y)
- Slope and Intercept
- RMSE and MAE
- R²
- Residual standard error
- Slope standard error
- t-value of slope

---

## API Reference

`LinearRegression(x, y)`

- **Parameters:**
  - `x` – 1D NumPy array of independent variable values.
  - `y` – 1D NumPy array of dependent variable values.
- **Description:** Initializes the linear regression model by fitting `y = a + b*x`.

| Method                  | Description                                                      |
| ----------------------- | ---------------------------------------------------------------- |
| `slope()`               | Returns the slope (b) of the regression line.                    |
| `intercept()`           | Returns the y-intercept (a) of the regression line.              |
| `predict(values)`       | Returns predicted `y` values for given `x` values.               |
| `predict_single(value)` | Returns the predicted `y` for a single `x` value.                |
| `rmse()`                | Returns Root Mean Squared Error.                                  |
| `mae()`                 | Returns Mean Absolute Error.                                      |
| `r_squared()`           | Returns coefficient of determination R².                          |
| `residual_std_error()`  | Returns residual standard error.                                   |
| `slope_standard_error()`| Returns standard error of the slope.                               |
| `t_value_slope()`       | Returns t-value for slope significance.                            |
| `summary()`             | Prints detailed regression statistics and error metrics.          |

---

## Notes

- Input arrays `x` and `y` must have the **same length**.
- Optimized with C++ for **speed on large datasets**.
- Simple and lightweight, focusing on **core linear regression functionality**.
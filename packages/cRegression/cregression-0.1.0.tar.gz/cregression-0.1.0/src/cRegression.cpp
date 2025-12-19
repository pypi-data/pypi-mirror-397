#include <cmath>
#include <iostream>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

namespace py = pybind11;

class LinearRegression {
  private:
    std::vector<double> x;
    std::vector<double> y;

    double sqr(double a) const { return a * a; }

  public:
    LinearRegression(py::array_t<double> x_array, py::array_t<double> y_array) {
        auto buf_x = x_array.request();
        auto buf_y = y_array.request();
        if (buf_x.size != buf_y.size)
            throw std::runtime_error("x and y must have the same length");

        x.resize(buf_x.size);
        y.resize(buf_y.size);
        double *ptr_x = (double *)buf_x.ptr;
        double *ptr_y = (double *)buf_y.ptr;
        for (size_t i = 0; i < buf_x.size; i++) {
            x[i] = ptr_x[i];
            y[i] = ptr_y[i];
        }
    }

    double mean_x() const {
        double sum = 0;
        for (double val : x) sum += val;
        return sum / x.size();
    }

    double mean_y() const {
        double sum = 0;
        for (double val : y) sum += val;
        return sum / y.size();
    }

    double pearson_correlation() const {
        double nom = 0, denom1 = 0, denom2 = 0;
        for (size_t i = 0; i < x.size(); i++) {
            nom    += (x[i] - mean_x()) * (y[i] - mean_y());
            denom1 += sqr(x[i] - mean_x());
            denom2 += sqr(y[i] - mean_y());
        }
        return nom / std::sqrt(denom1 * denom2);
    }

    double std_x() const {
        double sum = 0;
        double m   = mean_x();
        for (double val : x) sum += sqr(val - m);
        return std::sqrt(sum / (x.size() - 1));
    }

    double std_y() const {
        double sum = 0;
        double m   = mean_y();
        for (double val : y) sum += sqr(val - m);
        return std::sqrt(sum / (y.size() - 1));
    }

    double slope() const { return pearson_correlation() * (std_y() / std_x()); }
    double intercept() const { return mean_y() - slope() * mean_x(); }

    double predict_single(double value) const {
        return slope() * value + intercept();
    }

    std::vector<double> predict(const std::vector<double> &data) const {
        std::vector<double> result;
        for (double val : data) result.push_back(predict_single(val));
        return result;
    }

    double rmse() const {
        double sum  = 0;
        auto   pred = predict(x);
        for (size_t i = 0; i < y.size(); i++) sum += sqr(pred[i] - y[i]);
        return std::sqrt(sum / y.size());
    }

    double mae() const {
        double sum  = 0;
        auto   pred = predict(x);
        for (size_t i = 0; i < y.size(); i++) sum += std::abs(pred[i] - y[i]);
        return sum / y.size();
    }

    double r_squared() const {
        double nom = 0, denom = 0;
        auto   pred       = predict(x);
        double mean_y_val = mean_y();
        for (size_t i = 0; i < y.size(); i++) {
            nom   += sqr(pred[i] - y[i]);
            denom += sqr(y[i] - mean_y_val);
        }
        return 1.0 - nom / denom;
    }

    double residual_std_error() const {
        double sum  = 0;
        auto   pred = predict(x);
        for (size_t i = 0; i < y.size(); i++) sum += sqr(y[i] - pred[i]);
        return std::sqrt(sum / (x.size() - 2));
    }

    double slope_standard_error() const {
        double sum_x = 0;
        for (double val : x) sum_x += sqr(val - mean_x());
        return residual_std_error() / std::sqrt(sum_x);
    }

    double t_value_slope() const { return slope() / slope_standard_error(); }

    void summary() const {
        std::cout << "Mean(X): " << mean_x() << "\n";
        std::cout << "Mean(Y): " << mean_y() << "\n";
        std::cout << "Pearson correlation: " << pearson_correlation() << "\n";
        std::cout << "Std(X): " << std_x() << "\n";
        std::cout << "Std(Y): " << std_y() << "\n";
        std::cout << "Slope: " << slope() << "\n";
        std::cout << "Intercept: " << intercept() << "\n";
        std::cout << "RMSE: " << rmse() << "\n";
        std::cout << "MAE: " << mae() << "\n";
        std::cout << "R²: " << r_squared() << "\n";
        std::cout << "Residual Std Error: " << residual_std_error() << "\n";
        std::cout << "Slope Std Error: " << slope_standard_error() << "\n";
        std::cout << "t-value (slope): " << t_value_slope() << "\n";
    }
};

PYBIND11_MODULE(cRegression, m) {
    m.doc() = "Linear Regression with NumPy support";

    py::class_<LinearRegression>(m, "LinearRegression")
        .def(py::init<py::array_t<double>, py::array_t<double>>())
        .def("mean_x", &LinearRegression::mean_x)
        .def("mean_y", &LinearRegression::mean_y)
        .def("pearson_correlation", &LinearRegression::pearson_correlation)
        .def("std_x", &LinearRegression::std_x)
        .def("std_y", &LinearRegression::std_y)
        .def("slope", &LinearRegression::slope)
        .def("intercept", &LinearRegression::intercept)
        .def("predict_single", &LinearRegression::predict_single)
        .def("predict", &LinearRegression::predict)
        .def("rmse", &LinearRegression::rmse)
        .def("mae", &LinearRegression::mae)
        .def("r_squared", &LinearRegression::r_squared)
        .def("residual_std_error", &LinearRegression::residual_std_error)
        .def("slope_standard_error", &LinearRegression::slope_standard_error)
        .def("t_value_slope", &LinearRegression::t_value_slope)
        .def("summary", &LinearRegression::summary);
}

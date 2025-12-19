#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <spade_wrapper.h>  // From dtcc-pyspade-native
#include <vector>

namespace py = pybind11;

// Example function that uses Spade triangulation
py::dict triangulate_simple_polygon(py::array_t<double> polygon_array, double max_edge_length) {
    // Convert numpy array to Spade points
    auto buf = polygon_array.request();

    if (buf.ndim != 2 || buf.shape[1] < 2) {
        throw std::runtime_error("Input must be a 2D array with at least 2 columns");
    }

    std::vector<spade::Point> polygon;
    double* ptr = static_cast<double*>(buf.ptr);

    for (py::ssize_t i = 0; i < buf.shape[0]; i++) {
        double x = ptr[i * buf.shape[1] + 0];
        double y = ptr[i * buf.shape[1] + 1];
        double z = (buf.shape[1] >= 3) ? ptr[i * buf.shape[1] + 2] : 0.0;
        polygon.push_back({x, y, z});
    }

    // Use Spade for triangulation
    auto result = spade::triangulate(
        polygon,
        {},  // no holes
        {},  // no interior loops
        max_edge_length,
        spade::Quality::Moderate,
        true
    );

    // Convert result to Python dict with numpy arrays
    py::dict output;

    // Create vertices array
    py::array_t<double> vertices({result.num_vertices(), py::ssize_t(3)});
    auto v_ptr = static_cast<double*>(vertices.mutable_data());
    for (size_t i = 0; i < result.num_vertices(); i++) {
        v_ptr[i * 3 + 0] = result.points[i].x;
        v_ptr[i * 3 + 1] = result.points[i].y;
        v_ptr[i * 3 + 2] = result.points[i].z;
    }

    // Create triangles array
    py::array_t<size_t> triangles({result.num_triangles(), py::ssize_t(3)});
    auto t_ptr = static_cast<size_t*>(triangles.mutable_data());
    for (size_t i = 0; i < result.num_triangles(); i++) {
        t_ptr[i * 3 + 0] = result.triangles[i].v0;
        t_ptr[i * 3 + 1] = result.triangles[i].v1;
        t_ptr[i * 3 + 2] = result.triangles[i].v2;
    }

    output["vertices"] = vertices;
    output["triangles"] = triangles;
    output["num_vertices"] = result.num_vertices();
    output["num_triangles"] = result.num_triangles();

    return output;
}

PYBIND11_MODULE(_geometry_core, m) {
    m.doc() = "Example geometry module using Spade triangulation from dtcc-pyspade-native";

    m.def("triangulate", &triangulate_simple_polygon,
          "Triangulate a simple polygon",
          py::arg("polygon"),
          py::arg("max_edge_length") = 1.0);
}
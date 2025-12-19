import numpy as np

from .__prelude__ import ObservableStruct

TOLERANCE = 1e-6

class CurveEstimate(ObservableStruct):
    def __init__(self, curve, xs, ys):
        super().__init__()
        self.curve = curve
        self._current_params = np.array([param.initial for param in curve.params])
        self._min_params = np.array([param.min_bound for param in curve.params])
        self._max_params = np.array([param.max_bound for param in curve.params])
        not_nans = ~np.isnan(ys)
        self.xs = xs[not_nans]
        self.ys = ys[not_nans]

    def error(self, params = None):
        if params is None:
            params = self._current_params
        return self.curve.func(self.xs, *params) - self.ys
    def objective(self, params = None):
        err = self.error(params)
        return np.sum(err*err)

    @property
    def current_guess(self):
        return self._current_params

    def _clipped_step(self, delta):
        return np.clip(self._current_params + delta,
                       a_min = self._min_params,
                       a_max = self._max_params)

    def _linear_search(self, root_obj, grad):
        eta = 1.0
        best_obj = root_obj
        best_params = self._current_params
        while True:
            guess_params = self._clipped_step(-eta*grad)
            guess_obj = self.objective(guess_params)
            if guess_obj >= best_obj:
                break
            best_obj = guess_obj
            best_params = guess_params
            eta *= 2.0
        if eta == 1.0:
            while eta > 1e-20:
                guess_params = self._clipped_step(-eta*grad)
                guess_obj = self.objective(guess_params)
                if guess_obj < best_obj:
                    best_obj = guess_obj
                    best_params = guess_params
                    break
                eta *= 0.5

        if best_obj < root_obj:
            dparams = self._current_params - best_params
            self._current_params = best_params
            self.fieldChanged.emit('current_guess', None)
            return root_obj - best_obj > TOLERANCE
        else:
            return False

    def _obj_der(self, grad, delta):
        params = self._clipped_step(delta)
        err = self.error(params)
        d_obj = np.sum(2 * self.curve.jacobian(self.xs, *params) * err, axis=1)
        return -np.dot(grad, d_obj)

    def _data_at(self, grad, epsilon):
        delta = -epsilon*grad
        params = self._clipped_step(delta)
        obj = self.objective(params)
        der = self._obj_der(grad, delta)
        return params, obj, der

    def _bisection_search(self, root_obj, grad, right_epsilon):
        left_epsilon = 0.0
        left_params, left_obj, left_der = self._data_at(grad, left_epsilon)

        mid = right_epsilon
        mid_params, mid_obj, mid_der = self._data_at(grad, mid)
        while abs(mid_obj - left_obj) > TOLERANCE:
            if mid_obj > left_obj or mid_der >= 0.0:
                right_epsilon = mid
            else:
                left_epsilon, left_params, left_obj, left_der = mid, mid_params, mid_obj, mid_der
            mid = (right_epsilon + left_epsilon) * 0.5
            mid_params, mid_obj, mid_der = self._data_at(grad, mid)

        self._current_params = left_params
        return abs(root_obj - left_obj) > TOLERANCE

    def improve(self):
        err = self.error()
        d_fi = self.curve.jacobian(self.xs, *self._current_params)
        d_obj = 2 * d_fi * err
        grad = np.sum(d_obj, axis=1)
        norm2_grad = np.dot(grad, grad)
        cross_d2_obj = np.tensordot(grad, d_fi, axes=([0],[0]))
        cross_epsilon = np.sum(cross_d2_obj * cross_d2_obj)
        epsilon = norm2_grad / (2*(cross_epsilon + self.curve.hessian_epsilon(self.xs, err, grad, *self._current_params)))
        root_obj = np.sum(err*err)

        hess_params = self._clipped_step(-epsilon*grad)
        hess_obj = self.objective(hess_params)
        if epsilon > 0.0 and root_obj > hess_obj:
            self._current_params = hess_params
            return root_obj - hess_obj > TOLERANCE
        else:
            # if epsilon > 0.0:
            #     return self._bisection_search(root_obj, grad, epsilon)
            return self._linear_search(root_obj, grad)

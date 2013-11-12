/* Copyright 2013 Perttu Luukko

 * This file is part of libeemd.

 * libeemd is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * libeemd is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with libeemd.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "eemd.h"

// If we are using OpenMP for parallel computation, we need locks to ensure
// that the same output data is not written by several threads at the same
// time.
#ifdef _OPENMP
typedef omp_lock_t lock;
inline static void init_lock(lock* l) { omp_init_lock(l); }
inline static void destroy_lock(lock* l) { omp_destroy_lock(l); }
inline static void get_lock(lock* l) { omp_set_lock(l); }
inline static void release_lock(lock* l) { omp_unset_lock(l); }
#else
// If we don't use OpenMP, we provide a dummy lock that does nothing. This
// avoids littering the code with too many #ifdefs for _OPENMP.
typedef char lock;
inline static void init_lock(__attribute__((unused)) lock* l) {}
inline static void destroy_lock(__attribute__((unused)) lock* l) {}
inline static void get_lock(__attribute__((unused)) lock* l) {}
inline static void release_lock(__attribute__((unused)) lock* l) {}
#endif


// Helper functions for working with data arrays
inline static void array_copy(double const* src, size_t n, double* dest) {
	memcpy(dest, src, n*sizeof(double));
}

inline static void array_add(double const* src, size_t n, double* dest) {
	for (size_t i=0; i<n; i++)
		dest[i] += src[i];
}

inline static void array_sub(double const* src, size_t n, double* dest) {
	for (size_t i=0; i<n; i++)
		dest[i] -= src[i];
}

inline static void array_div(double* dest, size_t n, double val) {
	for (size_t i=0; i<n; i++)
		dest[i] /= val;
}

// Helper function for extrapolating data at the ends. For a line passing
// through (x0, y0), (x1, y1), and (x, y), return y for a given x.
inline static double linear_extrapolate(double x0, double y0,
		double x1, double y1, double x) {
	assert(x1 != x0);
	return y0 + (y1-y0)*(x-x0)/(x1-x0);
}

// Define a structure for memory required for each EMD run.
typedef struct {
	// The RNG
	gsl_rng* r;
	// Signal and previous residual for EMD
	double* x;
	double* res;
	// Found extrema
	double* maxx;
	double* maxy;
	double* minx;
	double* miny;
	// Upper and lower envelope spline values
	double* maxspline;
	double* minspline;
	// Extra memory required for spline evaluation.
	double* spline_workspace;
	// A pointer for shared locks. This is not initialized by the allocate
	// function!
	lock** locks;
} emd_workspace;

emd_workspace* allocate_emd_workspace(size_t N, unsigned long int rng_seed) {
	emd_workspace* w = malloc(sizeof(emd_workspace));
	w->r = gsl_rng_alloc(gsl_rng_mt19937);
	gsl_rng_set(w->r, rng_seed);
	w->x = malloc(N*sizeof(double));
	w->res = malloc(N*sizeof(double));
	w->maxx = malloc(N*sizeof(double));
	w->maxy = malloc(N*sizeof(double));
	w->minx = malloc(N*sizeof(double));
	w->miny = malloc(N*sizeof(double));
	w->maxspline = malloc(N*sizeof(double));
	w->minspline = malloc(N*sizeof(double));
	// Spline evaluation requires 5*m-10 doubles where m is the number of
	// extrema. The worst case scenario is that every point is an extrema, so
	// use m=N to be safe.
	const size_t spline_workspace_size = (N > 2)? 5*N-10 : 0;
	w->spline_workspace = malloc(spline_workspace_size*sizeof(double));
	return w;
}

void free_emd_workspace(emd_workspace* w) {
	free(w->spline_workspace); w->spline_workspace = NULL;
	free(w->minspline); w->minspline = NULL;
	free(w->maxspline); w->maxspline = NULL;
	free(w->miny); w->miny = NULL;
	free(w->minx); w->minx = NULL;
	free(w->maxy); w->maxy = NULL;
	free(w->maxx); w->maxx = NULL;
	free(w->res); w->res = NULL;
	free(w->x); w->x = NULL;
	gsl_rng_free(w->r); w->r = NULL;
	free(w);
}

// Helper function used internally for making a single EMD run with a
// preallocated workspace
static void _emd(emd_workspace* restrict w, size_t N, double* restrict output,
		unsigned int S_number, unsigned int num_siftings);

// Main EEMD decomposition routine definition
void eemd(double const* restrict input, size_t N, double* restrict output,
		unsigned int ensemble_size, double noise_strength, unsigned int
		S_number, unsigned int num_siftings) {
	assert(ensemble_size >= 1);
	assert(noise_strength >= 0);
	assert(ensemble_size == 1 || noise_strength > 0);
	assert(ensemble_size > 1 || noise_strength == 0);
	assert(S_number > 0 || num_siftings > 0);
	// For empty data we have nothing to do
	if (N == 0) {
		return;
	}
	const size_t M = emd_num_imfs(N);
	// Compute standard deviation of input data
	const double sigma = gsl_stats_sd(input, 1, N);
	const double noise_sigma = sigma*noise_strength;
	// Initialize output data to zero
	memset(output, 0x00, M*N*sizeof(double));
	// Each thread gets a separate workspace if we are using OpenMP
	emd_workspace** ws = NULL;
	// The locks are shared among all threads
	lock** locks;
	// Don't start unnecessary threads if the ensemble is small
	#ifdef _OPENMP
	if (omp_get_num_threads() > (int)ensemble_size) {
		omp_set_num_threads(ensemble_size);
	}
	#endif
	unsigned int ensemble_counter = 0;
	// The following section is executed in parallel
	#pragma omp parallel
	{
		#ifdef _OPENMP
		const int num_threads = omp_get_num_threads();
		const int thread_id = omp_get_thread_num();
		#if EEMD_DEBUG >= 1
		#pragma omp single
		fprintf(stderr, "Using %d thread(s) with OpenMP.\n", num_threads);
		#endif
		#else
		const int num_threads = 1;
		const int thread_id = 0;
		#endif
		#pragma omp single
		{
			ws = malloc(num_threads*sizeof(emd_workspace*));
			locks = malloc(M*sizeof(lock*));
			for (size_t i=0; i<M; i++) {
				locks[i] = malloc(sizeof(lock));
				init_lock(locks[i]);
			}
		}
		ws[thread_id] = allocate_emd_workspace(N, gsl_rng_default_seed+thread_id);
		emd_workspace* w = ws[thread_id];
		w->locks = locks;
		// Loop over all ensemble members, divinding them among the threads
		#pragma omp for
		for (size_t en_i=0; en_i<ensemble_size; en_i++) {
			// Initialize ensemble member as input data + noise
			if (noise_strength == 0.0) {
				array_copy(input, N, w->res);
			}
			else {
				for (size_t i=0; i<N; i++) {
					w->res[i] = input[i] + gsl_ran_gaussian(w->r, noise_sigma);
				}
			}
			// Extract IMFs with EMD
			_emd(w, N, output, S_number, num_siftings);
			#pragma omp atomic
			ensemble_counter++;
			#if EEMD_DEBUG >= 1
			fprintf(stderr, "Ensemble iteration %u/%u done.\n", ensemble_counter, ensemble_size);
			#endif
		}
		// Free resources
		free_emd_workspace(w);
		#pragma omp single
		{
			free(ws); ws = NULL;
			for (size_t i=0; i<M; i++) {
				destroy_lock(locks[i]);
				free(locks[i]);
			}
			free(locks); locks = NULL;
		}
	} // End of parallel block
	// Divide output data by the ensemble size to get the average
	if (ensemble_size != 1)
		array_div(output, N*M, ensemble_size);
}

static void _emd(emd_workspace* restrict w, size_t N, double* restrict output,
		unsigned int S_number, unsigned int num_siftings) {
	const size_t M = emd_num_imfs(N);
	// Provide some shorthands to avoid excessive '->' operators
	double* const x = w->x;
	double* const res = w->res;
	double* const maxx = w->maxx;
	double* const maxy = w->maxy;
	double* const minx = w->minx;
	double* const miny = w->miny;
	lock** locks = w->locks;
	for (size_t imf_i=0; imf_i<M-1; imf_i++) {
		array_copy(res, N, x);
		// Perform siftings
		unsigned int sift_counter = 0;
		unsigned int S_counter = 0;
		size_t num_max = (size_t)(-1);
		size_t num_min = (size_t)(-1);
		size_t prev_num_max = (size_t)(-1);
		size_t prev_num_min = (size_t)(-1);
		while (num_siftings == 0 || sift_counter < num_siftings) {
			sift_counter++;
			prev_num_max = num_max;
			prev_num_min = num_min;
			// Find extrema
			const bool all_extrema_good = emd_find_extrema(x, N,
					maxx, maxy, &num_max, minx, miny, &num_min);
			// Check if we are finished based on the S-number criteria
			if (S_number != 0) {
				if (all_extrema_good && (num_max == prev_num_max) && (num_min == prev_num_min)) {
					S_counter++;
					if (S_counter > S_number) {
						break;
					}
				}
				else {
					S_counter = 0;
				}
			}
			// Fit splines, choose order of spline based on number of extrema
			emd_evaluate_spline(maxx, maxy, num_max, w->maxspline, w->spline_workspace);
			emd_evaluate_spline(minx, miny, num_min, w->minspline, w->spline_workspace);
			// Subtract envelope mean from the data
			for (size_t i=0; i<N; i++) {
				x[i] -= 0.5*(w->maxspline[i] + w->minspline[i]);
			}
		}
		array_sub(x, N, res);
		/* Add results to output. Use locks to ensure other threads
		 are not writing to the same row of the output matrix at the same time */
		get_lock(locks[imf_i]);
		array_add(x, N, output+N*imf_i);
		release_lock(locks[imf_i]);
		#if EEMD_DEBUG >= 2
		fprintf(stderr, "IMF %zd saved after %u siftings.\n", imf_i+1, sift_counter);
		#endif
	}
	// Save final residual
	get_lock(locks[M-1]);
	array_add(res, N, output+N*(M-1));
	release_lock(locks[M-1]);
}

bool emd_find_extrema(double const* restrict x, size_t N,
		double* restrict maxx, double* restrict maxy, size_t* nmax,
		double* restrict minx, double* restrict miny, size_t* nmin) {
	// Handle empty array as a special case
	if (N == 0) {
		*nmax = 0;
		*nmin = 0;
		return true;
	}
	// Add the ends of the data as both local minima and extrema. These
	// might be changed later by linear extrapolation.
	maxx[0] = 0;
	maxy[0] = x[0];
	*nmax = 1;
	minx[0] = 0;
	miny[0] = x[0];
	*nmin = 1;
	// If we had only one data point this is it
	if (N == 1) {
		return true;
	}
	// Now starts the main extrema-finding loop. The loop detects points where
	// the slope of the data changes sign. In the case of flat regions at the
	// extrema, the center point of the flat region will be considered the
	// extremal point.
	bool all_extrema_good = true;
	enum slope { UP, DOWN, NONE };
	enum slope previous_slope = NONE;
	int flat_counter = 0;
	for (size_t i=0; i<N-1; i++) {
		if (x[i+1] > x[i]) { // Going up
			if (previous_slope == DOWN) {
				// Was going down before -> local minimum found
				minx[*nmin] = (double)(i)-(double)(flat_counter)/2;
				miny[*nmin] = x[i];
				(*nmin)++;
				if (x[i] >= 0) {
					all_extrema_good = false;
				}
			}
			previous_slope = UP;
			flat_counter = 0;
		}
		else if (x[i+1] < x[i]) { // Going down
			if (previous_slope == UP) {
				// Was going up before -> local maximum found
				maxx[*nmax] = (double)(i)-(double)(flat_counter)/2;
				maxy[*nmax] = x[i];
				(*nmax)++;
				if (x[i] <= 0) {
					all_extrema_good = false;
				}
			}
			previous_slope = DOWN;
			flat_counter = 0;
		}
		else { // Staying flat
			flat_counter++;
			#if EEMD_DEBUG >= 3
			fprintf(stderr, "Warning: a flat slope found in data. The results will differ from the reference EEMD implementation.\n");
			#endif
		}
	}
	// Add the other end of the data as extrema as well.
	maxx[*nmax] = N-1;
	maxy[*nmax] = x[N-1];
	(*nmax)++;
	minx[*nmin] = N-1;
	miny[*nmin] = x[N-1];
	(*nmin)++;
	// If we have at least two interior extrema, test if linear extrapolation provides
	// a more extremal value.
	if (*nmax >= 4) {
		const double max_el = linear_extrapolate(maxx[1], maxy[1],
				maxx[2], maxy[2], 0);
		if (max_el > maxy[0])
			maxy[0] = max_el;
		const double max_er = linear_extrapolate(maxx[*nmax-3], maxy[*nmax-3],
				maxx[*nmax-2], maxy[*nmax-2], N-1);
		if (max_er > maxy[*nmax-1])
			maxy[*nmax-1] = max_er;
	}
	if (*nmin >= 4) {
		const double min_el = linear_extrapolate(minx[1], miny[1],
				minx[2], miny[2], 0);
		if (min_el < miny[0])
			miny[0] = min_el;
		const double min_er = linear_extrapolate(minx[*nmin-3], miny[*nmin-3],
				minx[*nmin-2], miny[*nmin-2], N-1);
		if (min_er < miny[*nmin-1])
			miny[*nmin-1] = min_er;
	}
	return all_extrema_good;
}

size_t emd_num_imfs(size_t N) {
	if (N == 0) {
		return 0;
	}
	if (N <= 3) {
		return 1;
	}
	return (size_t)(log2(N));
}

void emd_evaluate_spline(double const* restrict x, double const* restrict y,
		size_t N, double* restrict spline_y, double* restrict spline_workspace) {
	const size_t n = N-1;
	const size_t max_j = (size_t)x[n];
	// perform some simple assertions
	assert(N >= 2);
	assert(x[0] == 0);
	for (size_t i=1; i<N; i++) {
		assert(x[i] > x[i-1]);
	}
	// Fall back to linear interpolation (for N==2) or polynomial interpolation
	// (for N==3)
	if (N <= 3) {
		gsl_poly_dd_init(spline_workspace, x, y, N);
		for (size_t j=0; j<=max_j; j++) {
			spline_y[j] = gsl_poly_dd_eval(spline_workspace, x, N, j);
		}
		return;
	}
	// For N >= 4, interpolate by using cubic splines with not-a-node end conditions.
	// This algorithm is described in "Numerical Algorithms with C" by
	// G. Engeln-Müllges and F. Uhlig, page 257.
	//
	// Extra homework assignment for anyone reading this: Implement this
	// algorithm in GSL, so that next time someone needs these end conditions
	// they can just use GSL.
	const size_t sys_size = N-2;
	double* const c = spline_workspace;
	double* const diag = c+N;
	double* const supdiag = diag + sys_size;
	double* const subdiag = supdiag + (sys_size-1);
	double* const g = subdiag + (sys_size-1);
	// Define some constants for easier comparison with Engeln-Mullges & Uhlig
	// and let the compiler optimize them away.
	const double h_0 = x[1]-x[0];
	const double h_1 = x[2]-x[1];
	const double h_nm1 = x[n]-x[n-1];
	const double h_nm2 = x[n-1]-x[n-2];
	// Describe the (N-2)x(N-2) linear system Ac=g with the tridiagonal
	// matrix A defined by subdiag, diag and supdiag
	// first row
	diag[0] = h_0 + 2*h_1;
	supdiag[0] = h_1 - h_0;
	g[0] = 3.0/(h_0 + h_1)*((y[2]-y[1]) - (h_1/h_0)*(y[1]-y[0]));
	// rows 2 to n-2
	for (size_t i=2; i<=n-2; i++) {
		const double h_i = x[i+1] - x[i];
		const double h_im1 = x[i] - x[i-1];
		
		subdiag[i-2] = h_im1;
		diag[i-1] = 2*(h_im1 + h_i);
		supdiag[i-1] = h_i;
		g[i-1] = 3.0*((y[i+1]-y[i])/h_i - (y[i]-y[i-1])/h_im1);
	}
	// final row
	subdiag[n-3] = h_nm2 - h_nm1;
	diag[n-2] = 2*h_nm2 + h_nm1;
	g[n-2] = 3.0/(h_nm1 + h_nm2)*((h_nm2/h_nm1)*(y[n]-y[n-1]) - (y[n-1]-y[n-2]));
	// Solve to get c_1 ... c_{n-1}
	gsl_vector_view diag_vec = gsl_vector_view_array(diag, n-1);
	gsl_vector_view supdiag_vec = gsl_vector_view_array(supdiag, n-2);
	gsl_vector_view subdiag_vec = gsl_vector_view_array(subdiag, n-2);
	gsl_vector_view g_vec = gsl_vector_view_array(g, n-1);
	gsl_vector_view solution_vec = gsl_vector_view_array(c+1, n-1);
	const int status = gsl_linalg_solve_tridiag(&diag_vec.vector,
			                                    &supdiag_vec.vector,
												&subdiag_vec.vector,
												&g_vec.vector,
												&solution_vec.vector);
	if (status) {
		fprintf(stderr, "Error reported by gsl_linalg_solve_tridiag: %s\n",
				gsl_strerror(status));
		return;
	}
	// Compute c[0] and c[n]
	c[0] = c[1] + (h_0/h_1)*(c[1]-c[2]);
	c[n] = c[n-1] + (h_nm1/h_nm2)*(c[n-1]-c[n-2]);
	// The coefficients b_i and d_i are computed from the c_i's, so just
	// evaluate the spline at the required points. In this case it is easy to
	// find the required interval for spline evaluation, since the evaluation
	// points j just increase monotonically from 0 to max_j.
	size_t i = 0;
	for (size_t j=0; j<=max_j; j++) {
		if (j > x[i+1]) {
			i++;
			assert(i < n);
		}
		const double dx = j-x[i];
		if (dx == 0) {
			spline_y[j] = y[i];
			continue;
		}
		// Compute coefficients b_i and d_i
		const double h_i = x[i+1] - x[i];
		const double a_i = y[i];
		const double b_i = (y[i+1]-y[i])/h_i - (h_i/3.0)*(c[i+1]+2*c[i]);
		const double c_i = c[i];
		const double d_i = (c[i+1]-c[i])/(3.0*h_i);
		// evaluate spline at x=j using the Horner scheme
		spline_y[j] = a_i + dx*(b_i + dx*(c_i + dx*d_i));
	}
}

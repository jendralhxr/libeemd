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

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gsl/gsl_math.h>
const double pi = M_PI;

#include "eemd.h"

const size_t ensemble_size = 250;
const unsigned int S_number = 4;
const unsigned int num_siftings = 0;
const double noise_strength = 0.2;
const unsigned long int rng_seed = 0;
const char outfile[] = "eemd_example.out";

// An example signal to decompose
const size_t N = 1024;
static inline double input_signal(double x) {
	const double omega = 2*pi/(N-1);
	return sin(17*omega*x)+0.5*(1.0-exp(-0.002*x))*sin(51*omega*x+1);
}

int main(void) {
	// Define input data
	double* inp = malloc(N*sizeof(double));
	for (size_t i=0; i<N; i++) {
		inp[i] = input_signal((double)i);
	}
	// Allocate memory for output data
	size_t M = emd_num_imfs(N);
	double* outp = malloc(M*N*sizeof(double));
	// Run eemd
	eemd(inp, N, outp, M, ensemble_size, noise_strength, S_number, num_siftings, rng_seed);
	// Write output to file
	FILE* fp = fopen(outfile, "w");
	for (size_t j=0; j<N; j++) {
		fprintf(fp, "%f ", inp[j]);
	}
	fprintf(fp, "\n");
	for (size_t i=0; i<M; i++) {
		for (size_t j=0; j<N; j++) {
			fprintf(fp, "%f ", outp[i*N+j]);
		}
		fprintf(fp, "\n");
	}
	printf("Done!\n");
	// Cleanup
	fclose(fp);
	free(inp); inp = NULL;
	free(outp); outp = NULL;
}

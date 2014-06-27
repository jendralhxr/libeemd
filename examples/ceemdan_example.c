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

const size_t ensemble_size = 500;
const unsigned int S_number = 4;
const unsigned int num_siftings = 0;
const double noise_strength = 0.02;
const unsigned long int rng_seed = 0;
const char outfile[] = "ceemdan_example.out";

const size_t N = 512;

int main(void) {
	// As an example decompose a Dirac signal as in the original CEEMDAN paper
	double* inp = malloc(N*sizeof(double));
	memset(inp, 0x00, N*sizeof(double));
	inp[N/2] = 1.0;
	// Allocate memory for output data
	size_t M = emd_num_imfs(N);
	double* outp = malloc(M*N*sizeof(double));
	// Run CEEMDAN
	ceemdan(inp, N, outp, ensemble_size, noise_strength, S_number, num_siftings, rng_seed);
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

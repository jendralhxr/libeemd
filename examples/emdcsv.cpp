// g++ emdcsv.cpp -leemd -lpthread
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gsl/gsl_math.h>
#include <eemd.h>
#include "csv.h"

const size_t ensemble_size = 250;
const unsigned int S_number = 4;
const unsigned int num_siftings = 50;
const double noise_strength = 0.2;
const unsigned long int rng_seed = 0;
char outfile[200];
// An example signal to decompose
const size_t N = 8160;
#define MARKERCOUNT 9
double centroid[MARKERCOUNT][8160], timeseries[8160];

int main(int argc, char **argv) {
	io::CSVReader<MARKERCOUNT+1> in(argv[1]);
	double temp;
	double val[10];
	//centroid = (double**) malloc(sizeof(double*)*MARKERCOUNT);
	for (int markernum=0; markernum<MARKERCOUNT; markernum++){
		//centroid[markernum] = (double*) malloc(sizeof(double));
		}
			
	// parse the signal
	int n=0, n_max;
	while (in.read_row(temp, \
	val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7], val[8] )) {
		//std::cout << time << ": " << val[4] << "," << val[6] << std::endl;
		for (int markernum=0; markernum<MARKERCOUNT; markernum++){
			//centroid[markernum]= (double*) realloc(centroid[markernum], sizeof(double) *n_max);
			centroid[markernum][n_max]= val[markernum];
			timeseries[n_max]= temp;
			}
		n_max++;
		std::cout << std::endl;
			
		}
	
	//std::cout << "number of elements: " << n_max << std::endl;
	for (int n=0; n<n_max; n++){
	//	std::cout << timeseries[n] << "," << centroid[4][n] << std::endl ;
		}
	
	libeemd_error_code err;
	
	size_t M = 10; // number of imfs
	double* outp = (double*)  malloc(M*n_max*sizeof(double));
	// Run eemd
	for (int k=0; k<MARKERCOUNT; k++){
	
	err = eemd(centroid[k], n_max, outp, M, ensemble_size, noise_strength, S_number, num_siftings, rng_seed);
	
		// Write output to file
		sprintf(outfile, "%s-%d", argv[1], k);
		FILE* fp = fopen(outfile, "w");
		for (size_t j=0; j<n_max; j++) {
		fprintf(fp, "%f,", timeseries[j]); 
		for (size_t i=0; i<M; i++) {
			fprintf(fp, "%f,", outp[i*N+j]);
			}
		fprintf(fp, "\n");
		}
		fclose(fp);
	}
	
	// Cleanup
	free(outp); outp = NULL;
	
}

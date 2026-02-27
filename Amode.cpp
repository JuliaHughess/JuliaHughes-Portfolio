#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <cmath>
#include <algorithm>
using namespace std;

float **createDataMatrix(int numElement, int numSample)
{
    // Create a 2D data matrix of size numElement and numSample
    float **RFData = new float*[numElement];
    for (int i = 0; i < numElement; i++)
    {
        RFData[i] = new float[numSample];
    }
    return RFData;
}

int loadRFData(float **RFData, const char *fileName, int numElement, int numSample)
{
    // Open the text file fileName, read the data and store into RFData
    // You can use the getline() command to extract the data lines from the txt files
    ifstream file(fileName);
    if (!file.is_open())
    {
        return -1; // Return -1 if the file could not be opened
    }

    for (int i = 0; i < numElement; i++)
    {
        for (int j = 0; j < numSample; j++)
        {
            char value[20];
            file.getline(value, 20, '\n');
            RFData[i][j] = atof(value);
        }
    }

    file.close();
    return 0; // Return 0 if the data is successfully loaded
}

float *genScanlineLocation(int &numPixel)
{
    float imagingDepth; //prompt user for how deep scalnline would be
    cout << "Enter the desired imaging depth: ";
    cin >> imagingDepth;
    cout << "Enter the number of pixels in the scanline: ";
    cin >> numPixel;

    float *scanlineLocation = new float[numPixel]; //Create an array with the first element representing the starting depth (at 0m)
    float increment = imagingDepth / (numPixel - 1);

    for (int i = 0; i < numPixel; i++)
    {
        scanlineLocation[i] = i * increment;
    }

    return scanlineLocation;
}

float *genElementLocation(int numElement, float PITCH)
{
    float *elementLocation = new float[numElement];// array with 128 elements

    for (int n = 0; n < numElement; n++)
    {
        elementLocation[n] = (n - ((numElement - 1) / 2.0)) * PITCH; //Formula for phsyical location (in x) of nth element of N-element array transducer
    }

    return elementLocation;
}

// Allocate memory to store the beamformed scanline
float *createScanline(int numPixel)
{
    float *scanline = new float[numPixel];
    return scanline;
}

// Beamform the A-mode scanline
void beamform(float *scanline, float **realRFData, float **imagRFData, float *scanlinePosition, float *elementPosition, int numElement, int numSample, int numPixel, float FS, float SoS)
{
    // Calculate forward and backward time of flight
    float *tforward = new float[numPixel];
    float **tbackward = new float*[numPixel];
    for (int i = 0; i < numPixel; i++)
    {
        tbackward[i] = new float[numElement];
    }

    // Calculate total time of flight and corresponding sample number
    int **s = new int*[numPixel];
    for (int i = 0; i < numPixel; i++)
    {
        s[i] = new int[numElement];
    }

    for (int i = 0; i < numPixel; i++)
    {
        tforward[i] = scanlinePosition[i] / SoS; //the time it takes for the wave to propagate from the transducer element to the imaging space.
        for (int k = 0; k < numElement; k++)
        {
            //Formula for calculating the time it takes for the ultrasound wave to travel from the ith scanline position back to the kth element of the transducer
            tbackward[i][k] = sqrt(pow(scanlinePosition[i], 2) + pow(elementPosition[k], 2)) / SoS; 
            //Formula for calculating what the total time of flight ttotal is from the transducer to the ith location and to the kth element
            float ttotal = tforward[i] + tbackward[i][k]; 
            //Formula to calculate which samples from kth transducer element matches with the ith scanline location
            s[i][k] = floor(ttotal * FS); 
        }
    }

    // Calculate the amplitude of the reflected wave
    for (int i = 0; i < numPixel; i++)
    {
        float Preal = 0.0, Pimag = 0.0;
        for (int k = 0; k < numElement; k++)
        {
            Preal += realRFData[k][s[i][k]];
            Pimag += imagRFData[k][s[i][k]];
        }
        scanline[i] = sqrt(pow(Preal, 2) + pow(Pimag, 2));
    }

    // Deallocate memory
    for (int i = 0; i < numPixel; i++)
    {
        delete[] tbackward[i];
        delete[] s[i];
    }
    delete[] tforward;
    delete[] tbackward;
    delete[] s;
}

// Write the scanline to a csv file
int outputScanline(const char *fileName, float *scanlinePosition, float *scanline, int numPixel) {
    // Create and open an output file
    ofstream outFile(fileName);

    // Check if the file was successfully opened
    if (!outFile.is_open()) {
        return -1; // Return -1 if the function failed to create or open the file
    }

    // Iterate through each of the scanline locations and scanline elements
    for (int i = 0; i < numPixel; i++) {
        // Store them into the output file
        outFile << scanlinePosition[i] << "," << scanline[i] << endl;
    }

    // Close the file
    outFile.close();

    return 0; // Return 0 if the function successfully wrote to the file
}

// Destroy all the allocated memory
void destroyAllArrays(float *scanline, float **realRFData, float **imagRFData, float *scanlinePosition, float *elementPosition, int numElement, int numSample, int numPixel)
{
    // Deallocate memory
    for (int i = 0; i < numElement; i++)
    {
        delete[] realRFData[i];
        delete[] imagRFData[i];
    }
    delete[] realRFData;
    delete[] imagRFData;
    delete[] scanlinePosition;
    delete[] elementPosition;
    delete[] scanline;
}


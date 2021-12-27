# deeplabcut-social-interaction

This is an application that cleans and wrangles the output from DeepLabCut and produces a CSV file containing information about rodent social interaction test. The application is adapted to the Eisch Lab's rodent social interaction protocol in which they perform a SI test on two mice within 1 trial (left and right mouse). 

The original model was trained on 200 frames that spanned across 4 videos. The model was trained for 200,000 iterations and has around a 95% accuracy.

This project was inspired by papers such as [Nagai, M., Nagai, H., Numa, C. et al. "Stress-induced sleep-like inactivity modulates stress susceptibility in mice"](https://www.nature.com/articles/s41598-020-76717-8?proof=t#citeas) and [Worley, Nicholas B., et al. “Deeplabcut Analysis of Social Novelty Preference.”](https://www.biorxiv.org/content/10.1101/736983v1)

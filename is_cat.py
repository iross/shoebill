#!/usr/bin/env python

#%HTCSS TEMPLATE
#executable=$(App)
#arguments= $(Image) $(Prediction)
#error=#(Error)
#log=is_cat.log
#request_cpus=$(Core)
#request_memory=$(Memory)
#transfer_output_files=cat_detection_model.pth
#request_disk=$(DiskSpace)
#%HTCSS TABLE
# jobN, Image, Prediction, Error, App, Core, Memory, DiskSpace
# 1, img001, img001_result.txt, 1.err, is_cat.py, 1, 2GB, 1GB
# 2, img002, img002_result.txt, 2.err, is_cat.py, 1, 2GB, 1GB
# 3, img003, img003_result.txt, 3.err, is_cat.py, 1, 2GB, 1GB
# 4, img004, img004_result.txt, 4.err, is_cat.py, 1, 2GB, 1GB
# 5, img005, img005_result.txt, 5.err, is_cat.py, 1, 2GB, 1GB
# 6, img006, img006_result.txt, 6.err, is_cat.py, 1, 2GB, 1GB
#%HTCSS END

import torch
import sys

def main():
    input_name, output_name = sys.argv[1:3]
    model = torch.load('cat_detection_model.pth')
    model.eval()
    is_cat(model, input_name, output_name)

def is_cat(model, image, result):
    image_tensor = torch.from_numpy(image).float().unsqueeze(0)
    output = model(image_tensor)
    cat_prob = torch.nn.functional.softmax(output, dim=-1)
    with open(output_name) as fout:
        fout.write(cat_prob)
    return 0

def train(images, labels):
    # generate a dummy model for detecting cats in an image
    model = torch.nn.Sequential(
        torch.nn.Conv2d(1, 10, kernel_size=5),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Flatten(),
        torch.nn.Linear(320, 50),
        torch.nn.ReLU(),
        torch.nn.Linear(50, 2)
    )
    # Load data and train the model
    data_loader = torch.utils.data.DataLoader(
        list(zip(images, labels)), batch_size=64, shuffle=True
    )
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    for epoch in range(10):  # number of epochs
        for batch_images, batch_labels in data_loader:
            optimizer.zero_grad()
            outputs = model(batch_images)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()


if __name__ == "__main__":
    main()

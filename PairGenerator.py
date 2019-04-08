import tkinter
import tkinter as ttk
import csv
import random
from os import path
import datetime

# Experiment Global Variables - Should be consistent between runs
label_pairs_directory = "../New_Assets/LabelPairs/"
reverse_percentage = 0.10
nonsense_percentage = 0.05
participant_name = ""
max_num_of_random_labels = 4
max_num_of_pairs = 6


class LabelPair:
    image_name = ""
    left_label = ""
    right_label = ""
    trial_type = ""

    def __init__(self, in_image_name, in_left_label, in_right_label, in_trial_type):
        self.image_name = in_image_name
        self.left_label = in_left_label
        self.right_label = in_right_label
        self.trial_type = in_trial_type


class SetParameters:
    def get_params(self):
        def save_parameters():
            global participant_name
            self.extension = file_extension.get()
            self.desc_path = desc_path_box.get()
            self.nonsense_path = nonsense_path_box.get()
            participant_name = res_path_box.get()
            now = datetime.datetime.now()
            self.label_pairs_path = label_pairs_directory + participant_name + "-label_pairs-" + str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "-" + \
                str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + ".tsv"
            window.destroy()

        window = tkinter.Tk()
        window.title("Set Experiment Parameters")
        frame = ttk.Frame(window)
        frame.grid(column="0", row="0", sticky=('N', 'W', 'E', 'S'))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        field_labels = ["File Extension (.jpg or .mp4)", "Description Location", "Participant Name", "Nonsense File Path"]

        file_extension = ttk.StringVar()
        desc_path_box = ttk.StringVar()
        res_path_box = ttk.StringVar()
        nonsense_path_box = ttk.StringVar()

        tkinter.Label(frame, text=field_labels[0]).grid(row=0, column=0, sticky='E')
        file_ext_entry = tkinter.Entry(frame, textvariable=file_extension)
        file_ext_entry.insert(0, '.mp4')
        file_ext_entry.grid(row=0, column=1, sticky='W')

        tkinter.Label(frame, text=field_labels[1]).grid(row=1, column=0, sticky='E')
        desc_entry = tkinter.Entry(frame, textvariable=desc_path_box)
        desc_entry.insert(0, '../New_Assets/Descriptions/training_video.tsv')
        desc_entry.grid(row=1, column=1, sticky='W')

        tkinter.Label(frame, text=field_labels[2]).grid(row=2, column=0, sticky='E')
        res_entry = tkinter.Entry(frame, textvariable=res_path_box)
        res_entry.insert(0, 'noname')
        res_entry.grid(row=2, column=1, sticky='W')

        tkinter.Label(frame, text=field_labels[3]).grid(row=3, column=0, sticky='E')
        nonsense_entry = tkinter.Entry(frame, textvariable=nonsense_path_box)
        nonsense_entry.insert(0, '../New_Assets/facts.tsv')
        nonsense_entry.grid(row=3, column=1, sticky='W')

        tkinter.Button(window, text="Run Experiment", command=save_parameters).grid(row=5)
        window.mainloop()

    def __init__(self):
        self.extension = ''
        self.desc_path = ''
        self.res_path = ''
        self.label_pairs_path = ''
        self.num_img = 0
        self.break_size = 0
        self.get_params()

class GeneratePairs:
    def get_labels(self, image):
        all_labels = self.descriptions[image]
        chosen_labels = []
        # Not randomized pairs - will be randomized and placed into self.label_pairs
        temp_pairs = list()
        # From all of the available descriptions, choose a subset of max_num_of_random_labels
        while len(chosen_labels) < max_num_of_random_labels:
            idx = random.randint(0, len(all_labels) - 1)
            if all_labels[idx] not in chosen_labels:
                chosen_labels.append(all_labels[idx])
        curr_num_of_pairs = 0
        # From the subset of pairs, create max_num_of_pairs amount of pairs
        for label_l in chosen_labels:
            for label_r in chosen_labels:
                if curr_num_of_pairs < max_num_of_pairs:
                    # Add to possible pairs if the chosen descriptions are not the same and
                    # both the same pair and the opposite does not exist
                    if label_l != label_r and (image, label_r, label_l, "Trial") not in self.label_pairs \
                            and (image, label_l, label_r, "Trial") not in self.label_pairs:
                        temp_pairs.append((image, label_l, label_r, "Trial"))
                        curr_num_of_pairs += 1
        # After the label pairs are created, randomly swap the description between the pairs
        while len(temp_pairs) != 0:
            curr_pair = temp_pairs.pop()
            choice = random.randint(0,1)
            # If 1, swap the values
            if choice == 1:
                # print("Swapping...") # Use to validate pairs have swapped
                # print("Before: ", curr_pair)
                # print("After: ", (curr_pair[0], curr_pair[2], curr_pair[1], curr_pair[3]))
                self.label_pairs.append((curr_pair[0], curr_pair[2], curr_pair[1], curr_pair[3]))
            else: # Leave the pairs as written by the program
                self.label_pairs.append((curr_pair[0], curr_pair[1], curr_pair[2], curr_pair[3]))

    def get_nonsense_list(self, num_of_nonsense, nonsense_path):
        nonsense = []
        with open(nonsense_path, 'r') as f:
            reader = csv.reader(f)
            temp = list(reader)
        for i, sentence in enumerate(temp):
            nonsense.append(sentence[0])
        final_list = []
        while len(final_list) < num_of_nonsense:
            final_list.append((random.choice(nonsense), "Nonsense"))
        return final_list

    def add_control_cases(self, nonsense_path):
        rev_pairs = []
        nonsense_pairs = []
        pair_holding = [] # Ensures that same pair isnt taken out twice per control
        print("Regular", len(self.label_pairs))
        # Reverse pair - 10% - Control 1
        num_rev_pairs = len(self.label_pairs) * reverse_percentage
        num_of_rev_controls = 0
        while len(rev_pairs) < num_rev_pairs:
            old_pair = self.label_pairs.pop(random.randint(0,len(self.label_pairs) - 1))
            old_pair = (old_pair[0], old_pair[1], old_pair[2], "Reverse Control " + str(num_of_rev_controls))
            new_pair = (old_pair[0], old_pair[2], old_pair[1], "Reverse Control " + str(num_of_rev_controls))
            pair_holding.append(old_pair)
            rev_pairs.append(new_pair)
            num_of_rev_controls += 1
        print("Reverse Controls", len(rev_pairs))
        # Nonsense pair - 5% - Control 2
        num_nonsense_pairs = len(self.label_pairs) * nonsense_percentage
        new_labels = self.get_nonsense_list(num_nonsense_pairs, nonsense_path)
        left_nonsense_pair = num_nonsense_pairs / 2
        right_nonsense_pair = num_nonsense_pairs - left_nonsense_pair
        new_labels_pos = 0
        while len(nonsense_pairs) < num_nonsense_pairs:
            old_pair = self.label_pairs.pop(random.randint(0,len(self.label_pairs) - 1))
            if left_nonsense_pair > 0:  # Left
                new_pair = (old_pair[0], new_labels[new_labels_pos], old_pair[2], "Nonsense Control - Left")
                left_nonsense_pair -= 1
            else:
                new_pair = (old_pair[0], old_pair[1], new_labels[new_labels_pos], "Nonsense Control - Right")
                right_nonsense_pair -= 1
            pair_holding.append(old_pair)
            nonsense_pairs.append(new_pair)
            new_labels_pos += 1
        while len(pair_holding) != 0:
            self.label_pairs.append(pair_holding.pop())
        print("Nonsense Pairs", len(nonsense_pairs))
        for new_pairs in rev_pairs:
            self.label_pairs.append(new_pairs)
        for new_pairs in nonsense_pairs:
            self.label_pairs.append(new_pairs)
        random.shuffle(self.label_pairs)
        print("Total pairs: ", len(self.label_pairs))


    def read_desc(self, desc_path):
        with open(desc_path, 'r') as f:
            reader = csv.reader(f, delimiter='\t') # TSV File
            temp = list(reader)
        temp = temp[1:]  # Remove table headers
        print(temp)
        for i in range(0,len(temp), 2):
            desc_row = temp[i]
            type_row = temp[i+1]
            if self.extension == '.jpg':
                file_name = 'i' + desc_row[0] + '.jpg'
            elif self.extension == '.mp4':
                file_name = desc_row[0] + '.mp4'
            else:
                print("INVALID EXTENSION. SUPPORT FOR ONLY .jpg OR .mp4")
            self.image_files.append(file_name)
            print(i, desc_row)
            for j in range(len(desc_row)):
                if j == 1:
                    self.descriptions[file_name] = list()
                if j != 0 and desc_row[j] != '':
                    if j >= len(type_row):
                        self.descriptions[file_name].append((desc_row[j], 'no_type_data_provided'))
                    else:
                        self.descriptions[file_name].append((desc_row[j], type_row[j]))


    def write_label_pairs(self,label_pairs_path):
        if path.isfile(label_pairs_path) is not True:
            with open(label_pairs_path, 'a') as csvfile:
                filewriter = csv.writer(csvfile, delimiter='\t',
                                        quotechar='\"', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(['Image Name', 'Left Label', 'Left Description', 'Right Label', 'Right Description', 'Pair Type'])
        with open(label_pairs_path, 'a') as csvfile:
            print(self.label_pairs)
            filewriter = csv.writer(csvfile, delimiter='\t',
                                    quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for pair in self.label_pairs[::-1]: # Reverse needed since label_pairs is treated as a queue in experiment
                left_desc = pair[1][0]
                left_type = pair[1][1]
                right_desc = pair[2][0]
                right_type = pair[2][1]
                filewriter.writerow([pair[0], left_desc, left_type, right_desc, right_type, pair[3]])

    def __init__(self, in_params):
        self.descriptions = {}
        self.extension = in_params.extension
        self.image_files = list()
        self.read_desc(in_params.desc_path)
        self.res_path = in_params.res_path
        self.label_pairs_path = in_params.label_pairs_path
        self.my_images = dict()
        self.label_pairs = list()
        for image in self.image_files:
            self.get_labels(image)
        self.add_control_cases(in_params.nonsense_path)
        self.write_label_pairs(in_params.label_pairs_path)


params = SetParameters()
GeneratePairs(params)

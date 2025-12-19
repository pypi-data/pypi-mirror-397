"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-11-22
----------------------------------------------------------------------
"""

from junshan_kit import ModelsHub

def check_args(self, args, parser, allowed_models, allowed_optimizers, allowed_datasets):
    # Parse and validate each train_group
    for cfg in args.train:
        try:
            model, dataset, optimizer = cfg.split("-")

            if model not in allowed_models:
                parser.error(f"Invalid model '{model}'. Choose from {allowed_models}")
            if optimizer not in allowed_optimizers:
                parser.error(f"Invalid optimizer '{optimizer}'. Choose from {allowed_optimizers}")
            if dataset not in allowed_datasets:
                parser.error(f"Invalid dataset '{dataset}'. Choose from {allowed_datasets}")

        except ValueError:
            parser.error(f"Invalid format '{cfg}'. Use model-dataset-optimizer")

    for cfg in args.train:
        model_name, dataset_name, optimizer_name = cfg.split("-")
        try:
            f = getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}")

        except:
            print(getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}"))
            assert False

def check_subset_info(self, args, parser):
        total = sum(args.subset)
        if args.subset[0]>1:
            # CHECK
            for i in args.subset:
                if i < 1:
                    parser.error(f"Invalid --subset {args.subset}: The number of subdata must > 1")    
        else:
            if abs(total - 1.0) != 0.0:  
                parser.error(f"Invalid --subset {args.subset}: the values must sum to 1.0 (current sum = {total:.6f}))")

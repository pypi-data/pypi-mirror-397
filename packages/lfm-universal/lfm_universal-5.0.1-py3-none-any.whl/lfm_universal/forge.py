
import torch
import torch.nn as nn

class ResonanceForge:
    @staticmethod
    def prune_model(model, efficiency=0.475):
        print(f"LFM FORGE: Applying {efficiency*100}% Geometric Pruning...")
        with torch.no_grad():
            for name, module in model.named_modules():
                if isinstance(module, nn.Linear):
                    W = module.weight.data
                    threshold = torch.std(W) * efficiency
                    mask = torch.abs(W).gt(threshold).float()
                    module.weight.data.mul_(mask)
        print("LFM FORGE: Logic Core Stabilized.")
        return model

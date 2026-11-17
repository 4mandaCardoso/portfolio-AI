"""LoRA mínimo: pesos base congelados e atualização W + escala * B @ A."""
import math
import torch
from torch import nn

class LoRALinear(nn.Module):
    def __init__(self, base, rank=8, alpha=16, dropout=0.05):
        super().__init__()
        self.base = base
        self.rank = rank
        self.scale = alpha / rank
        self.dropout = nn.Dropout(dropout)
        self.lora_A = nn.Parameter(torch.empty(rank, base.in_features, dtype=base.weight.dtype, device=base.weight.device))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, rank, dtype=base.weight.dtype, device=base.weight.device))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
    def forward(self, x):
        return self.base(x) + self.scale * torch.nn.functional.linear(torch.nn.functional.linear(self.dropout(x), self.lora_A), self.lora_B)

def attach(model, rank=8, alpha=16, dropout=0.05, targets=("q_proj", "v_proj")):
    for param in model.parameters():
        param.requires_grad = False
    replaced = []
    # Materializa a lista antes de modificar o grafo de módulos.
    for name, module in list(model.named_modules()):
        if isinstance(module, nn.Linear) and name.rsplit('.', 1)[-1] in targets:
            parent_name, child = name.rsplit('.', 1)
            setattr(model.get_submodule(parent_name), child, LoRALinear(module, rank, alpha, dropout))
            replaced.append(name)
    if not replaced:
        raise ValueError("O modelo não possui as projeções esperadas para LoRA.")
    return replaced

def adapter_state(model):
    return {name: param.detach().cpu().contiguous() for name,param in model.named_parameters() if '.lora_A' in name or '.lora_B' in name}

def load_adapter(model, state):
    expected = set(adapter_state(model))
    if set(state) != expected:
        raise ValueError("Pesos do adaptador incompatíveis com o modelo e configuração.")
    current = dict(model.named_parameters())
    with torch.no_grad():
        for name,value in state.items():
            if current[name].shape != value.shape:
                raise ValueError("Formato de peso LoRA incompatível.")
            current[name].copy_(value.to(current[name].device))

def merge(model):
    for name,module in list(model.named_modules()):
        if isinstance(module, LoRALinear):
            with torch.no_grad():
                module.base.weight.add_(module.scale * (module.lora_B @ module.lora_A))
            parent_name,child = name.rsplit('.',1)
            setattr(model.get_submodule(parent_name),child,module.base)
    return model

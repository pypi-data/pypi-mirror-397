import click
import sys
import os
import json
from pathlib import Path
from anc.cli.util import click_group, console
from .util import extract_step_from_path, \
                  get_custom_code_base_from_env, is_hf_ckpt, \
                  generate_eval_ckpt_list, \
                  generate_eval_dataset_list, \
                  generate_tasks_list, \
                  receipt_print_and_confirm, \
                  is_megatron_ckpt

from .util import WANDB_API_KEY

import uuid

from .operators.eval_operator import trigger_eval_job, display_evaluation_status, trigger_eval_sweep, eval_log_print, eval_stop
from typing import Optional, Set, Tuple
import re

 
@click_group()
def eval():
    pass

@eval.command()
@click.argument('model_name', required=True, type=str)
@click.option(
    '--dataset_paths', '--eval_dataset_paths',
    type=str,
    required=False,
    help='the eval dataset path of list/single of dataset'
)
@click.option(
    '--ckpt_paths',
    type=str,
    required=False,
    help='the eval ckpt path of list of ckpt'
)
@click.option(
    '--ckpt_list',
    type=str,
    required=False,
    help='comma-separated list of checkpoint full paths start with /mnt/project or /mnt/share'
)
@click.option(
    '--dataset_list', '--eval_dataset_list',
    type=str,
    required=False,
    help='comma-separated list of dataset full paths start with /mnt/project or /mnt/share'
)
@click.option(
    '--dataset_tasks', '--eval_tasks',
    type=str,
    required=False,
    help='string of dataset tasks, like "harness tasks: wikitext,games,reddits,openwebtext;hellaswag,truthfulqa"'
)
@click.option(
    '--tp', '--eval_tp',
    type=int,
    required=False,
    default=1,
    help='the evaltensor parallel size'
)
@click.option(
    '--pp', '--eval_pp',
    type=int,
    required=False,
    default=1,
    help='the eval pipeline parallel size'
)
@click.option(
    '--ep', '--eval_ep',
    type=int,
    required=False,
    default=1,
    help='the eval expert parallel size'
)
@click.option(
    '--seq_len', '--eval_seqlen', '--seq_length',
    type=int,
    required=False,
    default=1024,
    help='the eval sequence length'
)
@click.option(
    '--batch_size', '--eval_batch_size',
    type=int,
    required=False,
    default=1,
    help='the eval batch size'
)
@click.option(
    '--tokenizer_path', '--eval_tokenizer_path',
    type=str,
    default="",
    help='the project name'
)
@click.option(
    '--project_name',
    type=str,
    required=False,
    default="my_test",
    help='the project name'
)
@click.option(
    '--validation_batch_size',
    type=int,
    required=False,
    default=100000000,
    help='to control the max evaluation step on job side'
)
@click.option(
    '--task_eval_mode',
    type=click.Choice(['harness', 'opencompass', 'omni_eval']),
    required=False,
    default="harness",
    help='--task_eval_mode harness'
)
@click.option(
    '--harness_backend',
    required=False,
    type=click.Choice(['mix', 'nemo', 'vllm', 'mgt_lm'], case_sensitive=False),
    help='mix, nemo, vllm, where mix: use both nemo and vllm where vllm only for long context tasks',
    default='mix',
)
@click.option(
    '--omni_mode',
    required=False,
    type=str,
    help='omni mode: a2t or t2t',
    default="a2t",
)
@click.option(
    '--queue',
    type=str,
    required=False,
    default="default",
    help='different queue for different prority, auto_eval or default',
)
@click.option(
    '--model_args',
    type=str,
    required=False,
    default="",
    help='model args'
)
@click.option(
    '--wandb_project',
    type=str,
    required=False,
    default="None",
    help='wandb project name'
)
@click.option(
    '--training_framework',
    type=str,
    required=False,
    default="nemo",
    help='training framework: nemo or megatron, megatron is v2 version'
)
@click.option(
    '--task_degree_of_parallelism',
    type=int,
    required=False,
    default=100,
    help='the task degree of parallelism'
)
@click.option(
    '--private_eval_batch_size',
    type=int,
    required=False,
    default=1,
    help='to control the private eval batch size'
)
@click.pass_context
def model(ctx, 
          model_name, 
          ckpt_paths, 
          dataset_paths, 
          ckpt_list, 
          dataset_list,  # basically is harness tasks
          tp, 
          pp, 
          ep, 
          seq_len, 
          batch_size, 
          tokenizer_path, 
          project_name, 
          validation_batch_size,
          harness_backend,
          queue,
          omni_mode,
          dataset_tasks,
          task_eval_mode,
          model_args,
          wandb_project,
          training_framework,
          task_degree_of_parallelism,
          private_eval_batch_size):
    """command like: anc eval ds_v2 --ckpt_paths ckpt_paths --dataset_paths dataset_paths or --ckpt_list path1,path2 --dataset_list path1,path2"""
    
    # Validate that either paths or lists are provided, but not both
    if (ckpt_paths and ckpt_list) or (not ckpt_paths and not ckpt_list):
        print("Error: Please provide either --ckpt_paths OR --ckpt_list, but not both or neither")
        sys.exit(1)
    
    if (dataset_paths and dataset_list) or (not dataset_paths and not dataset_list and not dataset_tasks):
        print("Error: Please provide either --dataset_paths OR --dataset_list, but not both or neither")
        sys.exit(1)
    
    if not tokenizer_path and "tokenizer_path" not in model_args:
        print("Error: Please provide --tokenizer_path")
        sys.exit(1)
    
    # Process checkpoint paths
    eval_ckpt_paths_list = generate_eval_ckpt_list(ckpt_paths, ckpt_list)
    eval_ckpt_paths_list.sort(key=extract_step_from_path)
    
    # gen evlauation id from cli side.
    run_id = str(uuid.uuid4())

    eval_dataset_list = generate_eval_dataset_list(dataset_paths, dataset_list) 
    eval_tasks_list = generate_tasks_list(dataset_tasks)

    wandb_api_key = WANDB_API_KEY
    if not wandb_project:
        print("Warning: No wandb project name provided, wandb will not be used")
    # get custom code base from env
    custom_code_base_string = get_custom_code_base_from_env()

    is_megatron = is_megatron_ckpt(eval_ckpt_paths_list[0])
    training_framework = "nemo"
    if is_megatron:
        training_framework = "megatron"
        if  harness_backend == 'mix':
            harness_backend = "mgt_lm" # for v2, no mix anymore
    
    receipt_print_and_confirm(run_id,
                              model_name,
                              project_name,
                              tokenizer_path,
                              eval_ckpt_paths_list,
                              eval_dataset_list,
                              eval_tasks_list,
                              validation_batch_size,
                              harness_backend,
                              queue,
                              omni_mode,
                              wandb_project,
                              wandb_api_key,
                              custom_code_base_string,
                              tp,
                              pp,
                              seq_len,
                              task_eval_mode,
                              training_framework,
                              private_eval_batch_size,
                              batch_size)

    # for hf ckpt, force use vllm backend
    harness_backend = "vllm" if is_hf_ckpt(eval_ckpt_paths_list[0]) else harness_backend
    
    trigger_eval_job(run_id, 
                     model_name, 
                     project_name, 
                     eval_ckpt_paths_list,  # This is already a list
                     eval_dataset_list,  # This is already a list
                     tp,
                     pp,
                     ep,
                     seq_len,
                     batch_size,
                     tokenizer_path,
                     validation_batch_size,
                     dataset_tasks, # this is not a list, it is a string cancatenate tasks by ','
                     model_args,
                     wandb_project,
                     wandb_api_key,
                     custom_code_base_string,
                     harness_backend,
                     queue,
                     omni_mode,
                     task_eval_mode,
                     training_framework,
                     task_degree_of_parallelism)

@eval.command(name='status')
@click.argument('eval_id', required=True, type=str)
def status(eval_id):
   """check eval job: anc eval status xxx """
   display_evaluation_status(eval_id)


@eval.command()
@click.argument('spec', required=True, type=str)
@click.pass_context
def sweep(ctx, 
          spec):
    project = os.getenv("MLP_PROJECT", "llm")
    cluster = os.getenv("MLP_CLUSTER", "il2")
    trigger_eval_sweep(spec, cluster, project)

@eval.command()
@click.argument('evalution_id', required=True, type=str)
@click.pass_context
def log(ctx, 
          evalution_id):
    project = os.getenv("MLP_PROJECT", "llm")
    cluster = os.getenv("MLP_CLUSTER", "il2")
    eval_log_print(evalution_id, cluster)


@eval.command()
@click.argument('evalution_id', required=True, type=str)
@click.pass_context
def stop(ctx, 
          evalution_id):
    project = os.getenv("MLP_PROJECT", "llm")
    cluster = os.getenv("MLP_CLUSTER", "il2")
    eval_stop(evalution_id, cluster)


def add_command(cli_group):
    cli_group.add_command(eval)

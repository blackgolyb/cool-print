import numpy as np
from scipy import stats
import termcolor
import typing
from typing import Any


class Sample:
    def __init__(self, n : int, sigma : float, a : float):
        self.n = n
        self.sigma = sigma
        self.a = a
        
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self.generate()
            
        return self._data
    
    def generate(self):
        self._data = np.random.normal(self.a, self.sigma, self.n)
        return self._data
    
    


def get_parameter_from_formating_string(
    param_name: str,
    text: str,
    special_symbol : str = ':'
) -> [str, str]:
    param_pref = '{' + param_name
    parameter = None
    
    param_idx = text.find(param_pref)
    param_end_idx = text.find('}', param_idx)
    
    if text[param_idx+len(param_pref)] == special_symbol:
        parameter = text[param_idx+len(param_pref)+1 : param_end_idx]
        text = text.replace(f':{parameter}', '', 1)
        
    return text, parameter
    
    
def get_parameters_from_formating_string(text, special_symbol=':'):
    param_idx = -1
    params_info = dict()
    
    while True:
        param_idx = text.find('{', param_idx+1)
        if param_idx == -1:
            break
        
        param_name = ''
        i = param_idx + 1
        while True:
            current_char = text[i]
            if 'z' >= current_char.lower() >= 'a'\
                or '9' >= current_char.lower() >= '0'\
                or current_char == '_':
                    ...
            else:
                break
            
            param_name += current_char
            i += 1
            
        if param_name:
            text, param = get_parameter_from_formating_string(
                param_name=param_name,
                text=text,
                special_symbol=special_symbol
            )
            params_info[param_name] = param
            
    return text, params_info

# \\033\[[1-9]\d*m
def coloring_format_string(text, special_symbol=':'):
    text, params = get_parameters_from_formating_string(text, special_symbol=special_symbol)
    param_idx = -1
    
    while True:
        param_idx = text.find('{', param_idx+1)
        if param_idx == -1:
            break
        
        param_end_idx = text.find('}', param_idx)
        param_name = text[param_idx+1 : param_end_idx]
        if params[param_name] is not None:
            color = params[param_name]
            param = '{' + param_name + '}'
            colored_param = termcolor.colored(param, color=color)
            text = text[:param_idx] + colored_param + text[param_end_idx+1:]
        
        param_end_idx = text.find('}', param_end_idx)
        param_idx = param_end_idx
        
    return text

    
class Formater:
    def __call__(self, value: Any, **kwargs) -> str:
        return self.format(value, **kwargs)
        
    def format(self, value: Any) -> str:
        raise NotImplementedError
    
    
class SimpleFormater(Formater):
    fmt = '{value}'
    
    def __init__(self, fmt: str | None = None):
        self.fmt = fmt or self.fmt
        
    def format(self, value: Any) -> str:
        return self.fmt.format(value=value)


class FloatFormater(SimpleFormater):
    fmt = '{value:.5f}'
    
    
class TupleFormater(Formater):
    arguments_format = '  {argument},\n'
    index_format = '{index:red} |'
    expression_format = '(\n{expression}) len: {len}'
    long_arguments_format = '{start_arguments}  ...\n  {hidden_len} values\n  ...\n{end_arguments}' 
    is_long_shorting = True
    long_lenght = 20
    long_showing_section = 20
    
    def __init__(self):
        super().__init__()
        
        self.index_format = coloring_format_string(self.index_format)
        
    
    def format_long(self, value: tuple) -> str:
        showing_len = self.long_lenght // 2
        hidden_len = len(value) - showing_len * 2
        
        start_values = self._format_inner_values(value[:showing_len])
        end_values = self._format_inner_values(value[-showing_len:])
        
        start_values = ''.join(start_values)
        end_values = ''.join(end_values)
        
        expression = self.long_arguments_format.format(
            start_arguments=start_values,
            end_arguments=end_values,
            hidden_len=hidden_len,
        )
        return self.expression_format.format(
            expression=expression,
            len=len(value)
        )
        
    def numering_text(self, text):
        lines = text.split('\n')
        result = ''
        len_of_number = lambda num: len(str(num))
        
        
        for i, line in enumerate(lines):
            
            index = self.index_format.format(index=index)
            
            result += index + line + '\n'
            
        return result
    
    def _format_inner_values(self, value, use_idexes=True, add_to_index=0):
        formated_values = []
        max_len_of_index_number = len(str((len(value) - 1)))
        
        for i, inner_value in enumerate(value):
            formated_value = self.arguments_format.format(argument=inner_value)
            if use_idexes:
                index = f'{i:0{max_len_of_index_number}d}'.format(
                    i=add_to_index+i,
                )
                index = self.index_format.format(index=index)
                formated_value = index + formated_value
                
            formated_values.append(formated_value)
            
        return formated_values
        
    def format_short(self, value: tuple) -> str:
        formated_values = self._format_inner_values(value)
            
        formated_values = ''.join(formated_values)
        return self.expression_format.format(
            expression=formated_values,
            len=len(value)
        )
        
    def format(self, value: tuple, is_long_shorting: bool | None = None) -> str:
        if is_long_shorting is None:
            is_long_shorting = self.is_long_shorting
        
        if is_long_shorting and self.long_lenght <= len(value):
            return self.format_long(value)
            
        return self.format_short(value)
    
        
class ValueFormater(Formater):
    formaters : dict[Any, Formater] = {
        Any: SimpleFormater(),
        float: FloatFormater(),
        tuple: TupleFormater(),
    }
    
    def __init__(self, formaters : dict[Any, Formater] = {}):
        self.formaters.update(formaters)
    
    def _formaters_info(self):
        return formaters.keys()
    
    def format(self, value: Any, **kwargs) -> str:
        if type(value) in self.formaters:
            formater = self.formaters[type(value)]
            return formater(value, **kwargs)
        elif Any in self.formaters:
            formater = self.formaters[Any]
            return formater(value, **kwargs)
            
        raise ValueError('')


class CoolPrint:
    value_formater = ValueFormater()
    
    fmt = '{expression}{description}'
    variable_format = '{name:yellow} = {value:light_yellow}\n'
    value_format = '{value:light_yellow}\n'
    description_format = 'description: {description:light_blue}'
    default_color = 'blue'
    
    def __init__(self):
        # self.variable_format = termcolor.colored(self.variable_format, color=self.default_color)
        self.variable_format = coloring_format_string(self.variable_format)
        self.value_format = coloring_format_string(self.value_format)
        self.description_format = coloring_format_string(self.description_format)
        
    def _print_value(self, value, description=None):
        formated_value = self.value_format.format(
            value=value,
        )
        
        if description is None:
            description = ''
        else:
            description = self.description_format.format(description=description)
        
        text = self.fmt.format(
            expression=formated_value,
            description=description,
        )
        
        print(text)
        
    def _print_variable(self, value, name, description=None):
        formated_exp = self.variable_format.format(
            name=name,
            value=value,
        )
        
        if description is None:
            description = ''
        else:
            description = self.description_format.format(description=description)
            
        text = self.fmt.format(
            expression=formated_exp,
            description=description,
        )
        
        print(text)
    
    def _print(self, value, name=None, description=None):
        value = self.value_formater.format(value)
        
        if name is None:
            self._print_value(value, description)
            return
            
        self._print_variable(value, name, description)
        
    def __call__(self, value, **kwargs):
        self._print(value, **kwargs)
        
pp = CoolPrint()
pp(tuple([i for i in range(30)]))

# # variable_info_format = 
# pp(get_parameters_from_formating_string(variable_info_format))
pp(5.5666666666666666666666, name='hi!', description='hmmmmm...')


class Task:
    section_size : int = 60
    section_decor : str = '-'
    task_name : str = ''
    variable_info_format = '{name:yellow} = {variable:light_yellow}\ndescription: {description:light_blue}'
    
    def __init__(self):
        self.variable_info_format, self.name_colorize = self._format_for_color(
            'name',
            self.variable_info_format
        )
        self.variable_info_format, self.variable_colorize = self._format_for_color(
            'variable',
            self.variable_info_format
        )
        self.variable_info_format, self.description_colorize = self._format_for_color(
            'description',
            self.variable_info_format
        )
        self._variable_info_format = self.variable_info_format
        
    def _format_for_color(self, param_name, text):
        param_pref = '{' + param_name
        colorize = lambda text: text
        
        param_idx = text.find(param_pref)
        param_end_idx = text.find('}', param_idx)
        
        
        if text[param_idx+len(param_pref)] == ':':
            param_color = text[param_idx+len(param_pref)+1 : param_end_idx]
            colorize = lambda text: termcolor.colored(text, color=param_color)
            text = text.replace(f':{param_color}', '', 1)
            
        return text, colorize
        
    def run(self):
        raise NotImplementedError
    
    def print_section_text(self, text, **kwargs):
        section_decor = kwargs.get('section_decor', self.section_decor)
        
        remaining_length = self.section_size - len(text)
        before = section_decor * (remaining_length // 2)
        after = section_decor * (remaining_length // 2 + remaining_length % 2)
        formated_text = f'{before}{text}{after}'
        
        print(termcolor.colored(formated_text, **kwargs))
        
    def print_variable_info(self, var, name=None, description=None):
        if name is None:
            var = self.variable_colorize(str(var))
            if description is not None:
                idx = self._variable_info_format.find('{variable')
                _variable_info_format = self._variable_info_format[idx:]
                description = self.description_colorize(str(description))
                print(_variable_info_format.format(variable=var, description=description))
                return
            else:
                print(var)
                return
        
        name = self.name_colorize(str(name))
        var = self.variable_colorize(str(var))
        
        if description is None:
            idx = self._variable_info_format.find('{variable')
            idx = self._variable_info_format.find('}', idx)
            _variable_info_format = self._variable_info_format[:idx+1]
            print(_variable_info_format.format(name=name, variable=var))
        else:
            description = self.description_colorize(str(description))
            
            print(self._variable_info_format.format(name=name, variable=var, description=description))
    
    def show_info(self):
        self.print_section_text(self.task_name, color='green')
        
    def sub_info(self):
        ...
        
    def __call__(self, *args, **kwargs):
        # print(self.task_name)
        self.show_info()
        self.sub_info()
        self.run(*args, **kwargs)
        self.print_section_text('task_end', color='green')
        print()



class Task1(Task):
    task_name : str = 'Task1'
    
    def run(self, sample: Sample):
        n = sample.n
        sigma = sample.sigma
        a = sample.a
        random_numbers = sample.data
        
        conf_level = 0.95
        alpha = 1 - conf_level
        
        mean = np.mean(random_numbers)
        variance = np.var(random_numbers, ddof=1)
        std_deviation = np.std(random_numbers, ddof=1)
        
        self.print_variable_info(
            mean,
            'mean',
        )
        self.print_variable_info(
            variance,
            'variance'
        )
        self.print_variable_info(
            std_deviation,
            'std_deviation'
        )
        
        
        # Считаем доверительный интервал для мат ожтдания
        t_value = stats.t.ppf(1 - alpha / 2, n - 1)
        param = std_deviation / np.sqrt(n) * t_value
        
        mean_interval = (mean - param, mean + param)
        self.print_variable_info(
            mean_interval,
            'mean_interval'
        )


        # Считаем доверительный интервал для генеральной диспесии
        chi2_lower = stats.chi2.ppf((1 + alpha) / 2, n - 1)
        chi2_upper = stats.chi2.ppf((1 - alpha) / 2, n - 1)
        variance_interval = (
            (n - 1) * variance / chi2_lower,
            (n - 1) * variance / chi2_upper,
        )
        
        self.print_variable_info(
            variance_interval,
            'variance_interval'
        )
        
        
        # Считаем доверительный интервал для СКО
        std_interval = (
            (n - 1) * std_deviation / chi2_lower,
            (n - 1) * std_deviation / chi2_upper,
        )
        
        self.print_variable_info(
            std_interval,
            'std_interval'
        )


class Task2(Task):
    task_name : str = 'Task2'
    
    def run(self, sample: Sample):
        ...


def main():
    n = 100
    sigma = 3
    a = 5
    sample = Sample(n, sigma, a)
    
    Task1()(sample)
    Task2()(sample)

  
if __name__ == '__main__':
    main()

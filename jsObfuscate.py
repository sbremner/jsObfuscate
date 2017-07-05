import re
import sys
import string
import random


def get_random_string(length, choices = string.ascii_lowercase):
    s = ''
    
    for i in range(0, length):
        s += random.choice(choices)
        
    return s

    
def generate_template(js):
    length = len(js)
    
    variables = {
        'scriptDict': get_random_string(random.randint(5, 15)),
        'scriptSkip': random.randint(5,10),
        'obfScript': get_random_string(random.randint(5, 15)),
        'loopIndex': get_random_string(random.randint(5, 15)),
        'deobfScript': get_random_string(random.randint(5, 15)),
        'evalObf': get_random_string(random.randint(5, 15)),
        'evalDeobf': get_random_string(random.randint(5, 15)),
        'scriptSkipVar': get_random_string(random.randint(5, 15)),
        'scriptSkipPadding': random.randint(15, 25),
        'evalDecoy': get_random_string(random.randint(5, 15)),
        'rawEval': get_random_string(random.randint(5, 15))
    }
            
    script = '\n'.join([
        # Builds our embeded script (obfuscated by skipString - every nth char is the real script)
        'var {0} = {1};'.format(
            variables['obfScript'], obfuscate_boolInt(obfuscate_skipString(js, variables['scriptSkip'], variables['scriptSkipPadding'], False))
        ),
        
        # This is just a decoy variable used to confuse analysts
        'var {0} = {1};'.format(
            variables['evalDecoy'], obfuscate_charCode(get_random_string(random.randint(int(len(js)*0.75), int(len(js)*1.50))))
        ),
        
        # This is a loop variable we will use later for deobfuscation
        'var {0} = {1};'.format(variables['loopIndex'], variables['scriptSkipPadding']),
        
        # This is a pointless assignment to use our skip number for later
        'var {0} = {1};'.format(variables['scriptSkipVar'], variables['scriptSkip']),
        
        # This is where we will store the deobfuscated script
        'var {0} = "";'.format(variables['deobfScript']),
        
        # Gets obfuscated eval function name 'eval'
        'var {0} = {1};'.format(variables['rawEval'], obfuscate_boolInt('eval')),
        
        # This deobfuscates the above javascript and saves it as a new function which we will use later
        'var {0} = this[{1}];'.format(
            variables['evalDeobf'], variables['rawEval']
        ),
        
        # This is the loop that we will be using to deobfuscate our script
        '{0}'.format(deobfuscate_skipStringLoop(variables['loopIndex'], variables['obfScript'], variables['deobfScript'], variables['scriptSkipVar'])),
        
        # This is the call to eval(script) (NaN === NaN returns false)
        '(NaN === NaN ? {0} : {1})({2})'.format(
            variables['evalDecoy'], variables['evalDeobf'], variables['deobfScript']
        )
    ])
        
    return script


def get_nonalphanumeric(val):
    zero = '+[]'
    one = '+!+[]'
    
    (d,r) = divmod(val, 10)
    
    if d > 0:
        return '{0}+[{1}]'.format(get_nonalphanumeric(d), get_nonalphanumeric(r))
    else:
        if r == 0:
            return zero
        else:
            return '+[{0}]'.format((one * r))
    
    
def obfuscate_boolInt(s):
    data = []
    
    for i in range(0, len(s)):
        val = ord(s[i])
        
        data.append(get_nonalphanumeric(val))
    
    return "String.fromCharCode({0})".format(
        ','.join(data)
    )

    
def obfuscate_mixEncoding(s, percent_to_encode=50):
    obf = ''
    
    for i in range(0, len(s)):
        if random.randint(0, 100) <= percent_to_encode:
            obf += '\\u00{0:x}'.format(ord(s[i]))
        else:
            obf += s[i]
            
    return obf

    
def obfuscate_charCode(s, reverse=False):
    chCode = []
    
    for i in range(0, len(s)):
        chCode.append(ord(s[i]))
    
    if reverse is True:
        chCode.reverse()
    
    return "String.fromCharCode({0})".format(','.join(["{0}".format(ch) for ch in chCode]))


def deobfuscate_skipStringLoop(loopIndex, scriptIn, scriptOut, skip):
    return 'while({0} < {1}.length){{ {2} += {1}.charAt({0}); {0} += {3}; }}'.format(
            loopIndex, scriptIn, scriptOut, skip)

            
def obfuscate_skipString(js, skip, padding=0, double_escape=True):
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    
    obf = ''
    
    # Add padding if we so choose
    if padding > 0:
        obf += '{0}'.format(get_random_string(padding, choices))
    
    for i in range(0, len(js)):
        ch = js[i]

        if double_escape:
            if js[i] == '"':
                ch = '\\"'
            
            if js[i] == '\\':
                ch = '\\\\'
        
        obf += '{0}{1}'.format(ch, get_random_string(skip - 1, choices))    
    
    return obf

    
def handle_file(fname):

    with open(fname) as f:
        content = f.read()
        
        # Remove all of the new line characters
        content = content.replace('\n', '').replace('\r', '')
        # Remove duplicate whitespace
        content = re.sub('\s+', ' ', content).strip()
        
        print(generate_template(content))

        
def main(args):
   
    for fname in args:       
        handle_file(fname)
   

def startup():
    args = sys.argv[1:]

    if len(args) < 1:
        print('Error - input file names required')
        
    main(args)

    
if __name__ == "__main__":
    try:
        startup()
    except KeyboardInterrupt:
        print('User sent keyboard interrupt - exitting')
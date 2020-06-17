from io import BytesIO
from baudot import encode_str  # pip install baudot
from baudot.handlers import HexBytesWriter
from baudot.codecs import ITA2_STANDARD
import random


class Wheel:
    """ Class representing a single wheel. """

    def __init__(self, wheel_name, wheel_size, initial_position, wheel_data):
        self.wheel_name = str(wheel_name)
        self.wheel_data = wheel_data
        self.wheel_size = wheel_size
        self.current_position = initial_position

    def advance(self):
        self.current_position = (self.current_position + 1) % self.wheel_size

    def get_current_value(self):
        return self.wheel_data[self.current_position]

    def get_current_position(self):
        return self.current_position

    def get_config(self):
        return "wheel name: " + self.wheel_name + "; current_position: " + str(self.current_position) \
               + "; wheel_size: " + str(self.wheel_size) + "; wheel_data: " + str(self.wheel_data)


class WheelSet:
    """ Class for a set of wheels
    Each wheel set (K, S) has exactly 5 wheels
    except for Motor wheel set (M) which only has 2 wheels.
    """

    def __init__(self, *wheels):
        self.wheels = wheels

    def advance(self):
        for wheel in self.wheels:
            wheel.advance()

    def get_current_value(self):
        result = []
        for wheel_id in range(len(self.wheels)):
            result.append(self.wheels[wheel_id].get_current_value())

        # Here wheel having wheel_id=0 is the low significant bit
        # Hence result obtained above will be the reverse of actual result
        # Hence, result must be flipped

        result = result[::-1]
        return int('0b' + ''.join([str(i) for i in result]), base=2)

    def get_config(self):
        result = [wheel.get_config() for wheel in self.wheels]
        return '\n'.join(result)


class MotorWheelSet(WheelSet):
    """ Class for the motor (M) wheel set
    It is slightly different than other two wheel sets (K, S).
    Has 2 wheels. Rotation of M set decides whether S wheel set should advance
    """

    def __init__(self, *wheels):
        super().__init__(*wheels)

    def advance(self):
        self.wheels[0].advance()
        if self.wheels[0].get_current_value() == 1:
            self.wheels[1].advance()

    def is_active(self):
        """ return True if MSB of m_set is 1 else return False """
        return True if self.wheels[1].get_current_value() == 1 else False


class LorenzMachine:
    """ Represents an instance of a Lorenz Cipher Machine. """

    def __init__(self, k_set, s_set, m_set):
        self.k_set = k_set
        self.s_set = s_set
        self.m_set = m_set

    def advance(self):
        """ Advances the wheels by 1 position.
        Called after every encrypt or decrypt.
        """

        # k_set advance every time
        self.k_set.advance()

        # m_set "advance" every time.
        # Both M wheels do not advance at same iteration.
        self.m_set.advance()

        # s_set advance according to m_set
        if self.m_set.is_active():
            self.s_set.advance()

    def encrypt_character(self, char):
        """ Encrypt a single character. """

        result = char ^ self.k_set.get_current_value() ^ self.s_set.get_current_value()
        self.advance()
        return result

    def encrypt_message(self, message):
        """ Encrypt a Baudot encoded string message. """
        encrypted_message = [self.encrypt_character(number) for number in message]
        return '0b' + ''.join(['{0:05b}'.format(number) for number in encrypted_message])

    def get_config(self):
        return self.k_set.get_config(), self.s_set.get_config(), self.m_set.get_config()


if __name__ == '__main__':
    # generate random wheel_data
    def generate_wheel_data(seed, length):
        random.seed(seed)
        return [random.randint(0, 1) for _ in range(length)]


    # Task 1: Read any Wikipedia page with more than 1000 words encoded in ASCII.

    # Took first 1100 words from url: https://en.wikipedia.org/wiki/World_War_I
    # It is actually 'utf8' encoded
    actual_text = "World War I (often abbreviated as WWI or WW1), also known as the First World War or the Great War, was a global war originating in Europe that lasted from 28 July 1914 to 11 November 1918. Contemporaneously described as 'the war to end all wars', it led to the mobilisation of more than 70 million military personnel, including 60 million Europeans, making it one of the largest wars in history. It is also one of the deadliest conflicts in history, with an estimated nine million combatant and seven million civilian deaths as a direct result of the war, while resulting genocides and the related 1918 influenza pandemic caused another 17–50 million deaths worldwide. On 28 June 1914, Gavrilo Princip, a Bosnian Serb Yugoslav nationalist, assassinated the Austro-Hungarian heir Archduke Franz Ferdinand in Sarajevo, leading to the July Crisis. In response, on 23 July, Austria-Hungary issued an ultimatum to Serbia. Serbia's reply failed to satisfy the Austrians, and the two moved to a war footing. A network of interlocking alliances enlarged the crisis from a bilateral issue in the Balkans to one involving most of Europe. By July 1914, the great powers of Europe were divided into two coalitions: the Triple Entente—consisting of France, Russia, and Britain—and the Triple Alliance of Germany, Austria-Hungary, and Italy (the Triple Alliance was only defensive in nature, allowing Italy to stay out of the war until April 1915, when it joined the Allied Powers after its relations with Austria-Hungary deteriorated). Russia felt it necessary to back Serbia and, after Austria-Hungary shelled the Serbian capital of Belgrade on the 28 July, approved partial mobilisation. Full Russian mobilisation was announced on the evening of 30 July, on the 31st, Austria-Hungary and Germany did the same, while Germany demanded Russia demobilise within twelve hours. When Russia failed to comply, Germany declared war on Russia on 1 August in support of Austria-Hungary, with Austria-Hungary following suit on 6 August, France ordered full mobilisation in support of Russia on 2 August. German strategy for a war on two fronts against France and Russia was to rapidly concentrate the bulk of its army in the West to defeat France within six weeks, then shift forces to the East before Russia could fully mobilise, this was later known as the Schlieffen Plan. On 2 August, Germany demanded free passage through Belgium, an essential element in achieving a quick victory over France. When this was refused, German forces invaded Belgium on 3 August and declared war on France the same day, the Belgian government invoked the 1839 Treaty of London and in compliance with its obligations under this, Britain declared war on Germany on 4 August. On 12 August, Britain and France also declared war on Austria-Hungary, on the 23 August, Japan sided with Britain, seizing German possessions in China and the Pacific. In November 1914, the Ottoman Empire entered the war on the side of the Central Powers, opening fronts in the Caucasus, Mesopotamia, and the Sinai Peninsula. The war was fought in and drew upon each power's colonial empire as well, spreading the conflict to Africa and across the globe. The Entente and its allies would eventually become known as the Allied Powers, while the grouping of Austria-Hungary, Germany and their allies would become known as the Central Powers. The German advance into France was halted at the Battle of the Marne and by the end of 1914, the Western Front settled into a battle of attrition, marked by a long series of trench lines that changed little until 1917 (the Eastern Front, by contrast, was marked by much greater exchanges of territory). In 1915, Italy joined the Allied Powers and opened a front in the Alps. Bulgaria joined the Central Powers in 1915 and Greece joined the Allies in 1917, expanding the war in the Balkans. The United States initially remained neutral, though even while neutral it became an important supplier of war materiel to the Allies. Eventually, after the sinking of American merchant ships by German submarines, the declaration by Germany that its navy would resume unrestricted attacks on neutral shipping, and the revelation that Germany was trying to incite Mexico to make war on the United States, the U.S. declared war on Germany on 6 April 1917. Trained American forces would not begin arriving at the front in large numbers until mid-1918, but ultimately the American Expeditionary Force would reach some two million troops. Though Serbia was defeated in 1915, and Romania joined the Allied Powers in 1916 only to be defeated in 1917, none of the great powers were knocked out of the war until 1918. The 1917 February Revolution in Russia replaced the Tsarist autocracy with the Provisional Government, but continuing discontent with the cost of the war led to the October Revolution, the creation of the Soviet Socialist Republic, and the signing of the Treaty of Brest-Litovsk by the new government in March 1918, ending Russia's involvement in the war. This allowed the transfer of large numbers of German troops from the East to the Western Front, resulting in the German March 1918 Offensive. This offensive was initially successful but failed to score a decisive victory and exhausted the last of the German reserves. The Allies rallied and drove the Germans back in their Hundred Days Offensive, a continual series of attacks to which the Germans had no reply. Bulgaria was the first Central Power to sign an armistice—the Armistice of Salonica on 29 September 1918. On 30 October, the Ottoman Empire capitulated, signing the Armistice of Mudros. On 4 November, the Austro-Hungarian empire agreed to the Armistice of Villa Giusti. With its allies defeated, revolution at home, and the military no longer willing to fight, Kaiser Wilhelm abdicated on 9 November and Germany signed an armistice on 11 November 1918, effectively ending the war. World War I was a significant turning point in the political, cultural, economic, and social climate of the world. The war and its immediate aftermath sparked numerous revolutions and uprisings. The Big Four (Britain, France, the United States, and Italy) imposed their terms on the defeated powers in a series of treaties agreed at the 1919 Paris Peace Conference, the most well known being the German peace treaty—the Treaty of Versailles. Ultimately, as a result of the war the Austro-Hungarian, German, Ottoman, and Russian Empires ceased to exist, with numerous new states created from their remains. However, despite the conclusive Allied victory (and the creation of the League of Nations during the Peace Conference, intended to prevent future wars), a second world war would follow just over twenty years later."

    print('Actual_text:\n%s\n' % actual_text)

    # Task 2: Convert the page by re-encoding it in Baudot code.

    # converting `actual_text` to 'ascii' encoding
    # replaced non-ascii characters with ? to indicate a difference
    ascii_text = actual_text.encode(encoding='ascii', errors='replace').decode().upper()

    # converting `ascii_text` to hexa-decimal 'Baudot' encoding
    with BytesIO() as output_buffer:
        writer = HexBytesWriter(output_buffer)
        encode_str(chars=ascii_text, codec=ITA2_STANDARD, writer=writer)
        baudot_text = output_buffer.getvalue()

    # formatting and convert Baudot string to integer list
    baudot_text = baudot_text.decode()[2:]
    baudot_int_list = [int(baudot_text[i:i + 2], base=16) for i in range(0, len(baudot_text), 2)]

    # Baudot text as a binary

    baudot_text_binary = '0b' + ''.join(['{0:05b}'.format(number) for number in baudot_int_list])
    print('Baudot encoding in binary form: %s\n' % baudot_text_binary)

    # create a Lorenz machine

    # added specific seeds to random module to produce same random numbers every time
    seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    # wheel size
    k_size = [41, 31, 27, 26, 23]
    s_size = [43, 47, 51, 53, 59]
    m_size = [61, 37]

    # K wheel set
    k1 = Wheel(wheel_name='k1', wheel_size=k_size[0], initial_position=0,
               wheel_data=generate_wheel_data(seeds[0], length=k_size[0]))
    k2 = Wheel(wheel_name='k2', wheel_size=k_size[1], initial_position=0,
               wheel_data=generate_wheel_data(seeds[1], length=k_size[1]))
    k3 = Wheel(wheel_name='k3', wheel_size=k_size[2], initial_position=0,
               wheel_data=generate_wheel_data(seeds[2], length=k_size[2]))
    k4 = Wheel(wheel_name='k4', wheel_size=k_size[3], initial_position=0,
               wheel_data=generate_wheel_data(seeds[3], length=k_size[3]))
    k5 = Wheel(wheel_name='k5', wheel_size=k_size[4], initial_position=0,
               wheel_data=generate_wheel_data(seeds[4], length=k_size[4]))
    k_set = WheelSet(k1, k2, k3, k4, k5)

    # S wheel set
    s1 = Wheel(wheel_name='s1', wheel_size=s_size[0], initial_position=0,
               wheel_data=generate_wheel_data(seeds[5], length=s_size[0]))
    s2 = Wheel(wheel_name='s2', wheel_size=s_size[1], initial_position=0,
               wheel_data=generate_wheel_data(seeds[6], length=s_size[1]))
    s3 = Wheel(wheel_name='s3', wheel_size=s_size[2], initial_position=0,
               wheel_data=generate_wheel_data(seeds[7], length=s_size[2]))
    s4 = Wheel(wheel_name='s4', wheel_size=s_size[3], initial_position=0,
               wheel_data=generate_wheel_data(seeds[8], length=s_size[3]))
    s5 = Wheel(wheel_name='s5', wheel_size=s_size[4], initial_position=0,
               wheel_data=generate_wheel_data(seeds[9], length=s_size[4]))
    s_set = WheelSet(s1, s2, s3, s4, s5)

    # M wheel set
    m1 = Wheel(wheel_name='m1', wheel_size=m_size[0], initial_position=0,
               wheel_data=generate_wheel_data(seeds[10], length=m_size[0]))
    m2 = Wheel(wheel_name='m2', wheel_size=m_size[1], initial_position=0,
               wheel_data=generate_wheel_data(seeds[11], length=m_size[1]))
    m_set = MotorWheelSet(m1, m2)

    # Task 3: Encrypt the contents using the Lorenz keystream generator

    # Initiating Lorenz machine
    lorenz_machine = LorenzMachine(k_set=k_set, s_set=s_set, m_set=m_set)

    # printing configuration of wheels
    k_config, s_config, m_config = lorenz_machine.get_config()
    print('Machine configuration:\n%s\n%s\n%s\n' % (k_config, s_config, m_config))

    encrypted_message = lorenz_machine.encrypt_message(baudot_int_list)
    print('Encrypted message in binary form: %s\n' % encrypted_message)

    # Task 4: Compute the number of bits from the input plaintext that was changed in the ciphertext as a percentage.

    difference = 0
    for index in range(len(encrypted_message[2:])):
        difference += 1 if encrypted_message[2:][index] == baudot_text_binary[2:][index] else 0
    print('Change of bits due to encryption: %.2f percentage'
          % (round(difference / len(encrypted_message[2:]) * 100, 2)))
